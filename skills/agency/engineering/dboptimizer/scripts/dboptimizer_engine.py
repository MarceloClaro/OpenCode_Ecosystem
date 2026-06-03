"""DatabaseOptimizer Engine — SQL schema/query analysis and optimization.

Extracted from agency-agents/engineering/engineering-database-optimizer.md
Round 14 Evolution — Agency Engineering Domain
"""

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SchemaAnalysis:
    tables: list[dict]
    missing_indexes: list[str]
    type_warnings: list[dict]
    score: int
    available: bool = True


@dataclass
class NPlusOneReport:
    occurrences: list[dict]
    count: int
    available: bool = True


@dataclass
class IndexSuggestions:
    suggestions: list[dict]
    count: int
    available: bool = True


@dataclass
class AntipatternReport:
    antipatterns: list[dict]
    count: int
    available: bool = True


class DatabaseOptimizer:
    """Analyzes SQL schemas, queries, N+1 patterns, and antipatterns."""

    QUERY_KEYWORDS = {'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE'}

    ANTIPATTERNS = [
        (r'(?i)SELECT\s+\*\s+FROM', 'SELECT * — avoid, list columns explicitly', 'MEDIUM'),
        (r"(?i)WHERE\s+\w+\s+LIKE\s+'%[^%]",
         "LIKE with leading wildcard — cannot use B-tree index", 'HIGH'),
        (r'(?i)WHERE\s+(?:UPPER|LOWER|TRIM|DATE|YEAR|MONTH)\s*\(',
         'Function on column in WHERE — prevents index usage', 'HIGH'),
        (r'(?i)FROM\s+(\w+)\s*,\s*(\w+)\s+WHERE',
         'Implicit CROSS JOIN — use explicit JOIN syntax', 'MEDIUM'),
        (r'(?i)ORDER\s+BY\s+RAND\s*\(\s*\)',
         'ORDER BY RAND() — extremely slow on large tables', 'HIGH'),
        (r'(?i)WHERE\s+\w+\s*(?:!=|<>)\s*',
         'Negative comparison (!= / <>) — prevents index usage in many engines', 'LOW'),
        (r'(?i)GROUP\s+BY\s+\d+',
         'GROUP BY ordinal position — fragile, use column names', 'LOW'),
        (r'(?i)HAVING\s+\w+\s*[=<>].+(?!.*GROUP\s+BY)',
         'HAVING without GROUP BY — use WHERE instead', 'MEDIUM'),
    ]

    TYPE_WARNINGS = {
        'TEXT': ('TEXT used for short field — consider VARCHAR(n)', 'MEDIUM'),
        r'VARCHAR\((\d{4,})\)': ('VARCHAR with large limit — verify necessity', 'LOW'),
        'BLOB': ('BLOB type — consider if binary storage is needed', 'LOW'),
    }

    INDEXABLE_CLAUSES = ['WHERE', 'JOIN', 'ON', 'ORDER BY', 'GROUP BY']

    @property
    def available(self) -> bool:
        return True

    def analyze_schema(self, ddl_text: str) -> SchemaAnalysis:
        tables: list[dict] = []
        missing_indexes: list[str] = []
        type_warnings: list[dict] = []
        score = 100

        table_blocks = re.split(r'(?i);\s*\n\s*CREATE\s+TABLE', ddl_text)
        for block in table_blocks:
            if not block.strip().upper().startswith('CREATE TABLE'):
                if 'CREATE TABLE' not in block.upper():
                    block = 'CREATE TABLE ' + block

            table_match = re.search(
                r'(?i)CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)',
                block,
            )
            if not table_match:
                continue

            table_name = table_match.group(1)
            columns = re.findall(r'^\s*(\w+)\s+(\w+(?:\(\d+(?:,\d+)?\))?)', block, re.MULTILINE)
            col_info: list[dict] = []
            indexes_found: list[str] = []
            has_primary = False

            for col_name, col_type in columns:
                col_info.append({'name': col_name, 'type': col_type.upper()})

                for type_pat, (msg, sev) in self.TYPE_WARNINGS.items():
                    if re.search(type_pat, col_type.upper()):
                        type_warnings.append({
                            'table': table_name,
                            'column': col_name,
                            'type': col_type,
                            'message': msg,
                            'severity': sev,
                        })
                        score -= 5

            for idx_match in re.finditer(
                r'(?i)(PRIMARY\s+KEY|INDEX|UNIQUE|FOREIGN\s+KEY)\s*(?:(\w+)\s*)?\(([^)]+)\)',
                block,
            ):
                idx_type = idx_match.group(1).upper()
                idx_cols = idx_match.group(3)
                indexes_found.append(f'{idx_type}({idx_cols})')
                if 'PRIMARY' in idx_type:
                    has_primary = True

            if col_info and not has_primary:
                missing_indexes.append(
                    f'ALTER TABLE {table_name} ADD PRIMARY KEY (id); -- no primary key detected'
                )
                score -= 15

            fk_refs = re.findall(r'(?i)FOREIGN\s+KEY\s*\((\w+)\)\s*REFERENCES\s*(\w+)\((\w+)\)', block)
            for fk_col, ref_table, ref_col in fk_refs:
                idx_on_fk = any(fk_col in idx for idx in indexes_found if 'INDEX' in idx or 'KEY' in idx)
                if not idx_on_fk:
                    missing_indexes.append(
                        f'CREATE INDEX idx_{table_name}_{fk_col} ON {table_name}({fk_col});'
                    )
                    score -= 5

            tables.append({
                'name': table_name,
                'columns': col_info,
                'indexes': indexes_found,
                'warnings': [w for w in type_warnings if w['table'] == table_name],
            })

        return SchemaAnalysis(
            tables=tables,
            missing_indexes=missing_indexes,
            type_warnings=type_warnings,
            score=max(0, score),
        )

    def detect_n_plus_one(self, source_code: str) -> NPlusOneReport:
        occurrences: list[dict] = []
        lines = source_code.split('\n')

        loop_pattern = re.compile(
            r'^\s*(for|while|forEach|\.map\s*\(|\.each\s*\()',
        )
        query_pattern = re.compile(
            r'(?:\.find|\.all|\.get|\.execute|\.query|SELECT|INSERT|UPDATE|DELETE)',
            re.IGNORECASE,
        )

        in_loop = False
        loop_start = 0
        loop_type = ''

        for i, line in enumerate(lines):
            if loop_pattern.search(line):
                in_loop = True
                loop_start = i + 1
                loop_type = loop_pattern.search(line).group(1)
                continue

            if in_loop and line.strip() == '' and i - loop_start > 10:
                in_loop = False
                continue

            if in_loop and query_pattern.search(line):
                occurrences.append({
                    'line': i + 1,
                    'loop_type': loop_type,
                    'query': line.strip()[:120],
                    'suggestion': 'Use eager loading, batch query, or JOIN to avoid N+1',
                })

        return NPlusOneReport(occurrences=occurrences, count=len(occurrences))

    def suggest_indexes(self, ddl_text: str, queries: list[str]) -> IndexSuggestions:
        suggestions: list[dict] = []
        table_cols: dict[str, set[str]] = {}

        for block in re.split(r'(?i);\s*\n\s*CREATE\s+TABLE', ddl_text):
            if not block.strip().upper().startswith('CREATE TABLE'):
                if 'CREATE TABLE' not in block.upper():
                    block = 'CREATE TABLE ' + block

            table_match = re.search(
                r'(?i)CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)',
                block,
            )
            if table_match:
                table_name = table_match.group(1)
                cols = re.findall(r'^\s*(\w+)\s+\w+', block, re.MULTILINE)
                table_cols[table_name] = set(cols)

        existing_indexes: set[tuple[str, str]] = set()
        for block in re.split(r'(?i);\s*\n\s*CREATE\s+TABLE', ddl_text):
            idx_matches = re.findall(
                r'(?i)(?:INDEX|KEY)\s+(\w+)\s*\((\w+)\)',
                block,
            )
            for _, col in idx_matches:
                if table_match:
                    existing_indexes.add((table_match.group(1), col.lower()))

        for query in queries:
            table_matches = re.findall(
                r'(?i)(?:FROM|JOIN)\s+(\w+)', query
            )
            tables_in_q = [t for t in table_matches if t.lower() not in ('select', 'where')]

            where_cols = re.findall(
                r'(?i)WHERE\s+(?:\w+\.)?(\w+)\s*[=<>]', query
            )
            join_cols = re.findall(
                r'(?i)(?:ON|USING)\s*\(\s*(?:\w+\.)?(\w+)', query
            )
            order_cols = re.findall(
                r'(?i)ORDER\s+BY\s+(?:\w+\.)?(\w+)', query
            )

            candidate_cols = where_cols + join_cols + order_cols

            for table in tables_in_q:
                if table not in table_cols:
                    continue
                for col in set(candidate_cols):
                    if col in table_cols[table] and (table, col.lower()) not in existing_indexes:
                        suggestions.append({
                            'table': table,
                            'columns': [col],
                            'ddl': f'CREATE INDEX idx_{table}_{col} ON {table}({col});',
                            'reason': f'Column used in WHERE/JOIN/ORDER BY without index',
                        })
                        existing_indexes.add((table, col.lower()))

        return IndexSuggestions(suggestions=suggestions, count=len(suggestions))

    def detect_antipatterns(self, query_text: str) -> AntipatternReport:
        antipatterns: list[dict] = []
        queries = re.split(r';\s*\n', query_text)

        line_offset = 0
        for query in queries:
            query_lines = query.split('\n')
            for i, line in enumerate(query_lines):
                abs_line = line_offset + i + 1
                for pattern, description, severity in self.ANTIPATTERNS:
                    if re.search(pattern, line):
                        antipatterns.append({
                            'line': abs_line,
                            'pattern': description,
                            'severity': severity,
                            'fix': self._get_fix(description),
                        })
            line_offset += len(query_lines)

        return AntipatternReport(antipatterns=antipatterns, count=len(antipatterns))

    def _get_fix(self, description: str) -> str:
        fixes = {
            'SELECT *': 'List specific columns instead of *',
            'LIKE with leading': 'Consider full-text search index or remove leading wildcard',
            'Function on column': 'Move function to the comparison value, or use a functional index',
            'Implicit CROSS': 'Use explicit JOIN ... ON syntax',
            'ORDER BY RAND()': 'Use application-level randomization or TABLESAMPLE',
            'Negative comparison': 'Rewrite as IN or EXISTS if possible for index usage',
            'GROUP BY ordinal': 'Use explicit column names in GROUP BY',
            'HAVING without': 'Move condition to WHERE clause',
        }
        for key, fix in fixes.items():
            if key in description:
                return fix
        return 'Review and refactor the query structure'
