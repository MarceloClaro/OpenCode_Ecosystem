"""Data Consolidation Agent Engine -- Schema alignment, merging, and aggregation."""

from __future__ import annotations

from enum import Enum
from dataclasses import dataclass, field
from collections import Counter


class AggFunc(Enum):
    SUM = "sum"
    AVG = "avg"
    COUNT = "count"
    MIN = "min"
    MAX = "max"


@dataclass
class ColumnSchema:
    name: str
    dtype: str
    nullable: bool = True

    @property
    def is_numeric(self) -> bool:
        return self.dtype in ("int", "float", "integer", "number")

    @property
    def is_text(self) -> bool:
        return self.dtype in ("str", "string", "text")


@dataclass
class SourceSchema:
    source_name: str
    columns: list[ColumnSchema] = field(default_factory=list)

    @property
    def column_names(self) -> set[str]:
        return {c.name for c in self.columns}

    @property
    def numeric_columns(self) -> list[str]:
        return [c.name for c in self.columns if c.is_numeric]


@dataclass
class ConsolidationResult:
    merged_rows: list[dict]
    source_counts: Counter = field(default_factory=Counter)
    warnings: list[str] = field(default_factory=list)

    @property
    def total_rows(self) -> int:
        return len(self.merged_rows)

    @property
    def source_breakdown(self) -> dict:
        return dict(self.source_counts)

    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0


@dataclass
class DataConsolidator:
    sources: dict[str, SourceSchema] = field(default_factory=dict)

    def register_source(self, schema: SourceSchema) -> bool:
        if schema.source_name in self.sources:
            return False
        self.sources[schema.source_name] = schema
        return True

    @property
    def common_columns(self) -> set[str]:
        if not self.sources:
            return set()
        cols = [s.column_names for s in self.sources.values()]
        return cols[0].intersection(*cols[1:]) if len(cols) > 1 else cols[0]

    def merge(self, datasets: dict[str, list[dict]], key_column: str) -> ConsolidationResult:
        result = ConsolidationResult(merged_rows=[], warnings=[])
        seen_keys: set = set()

        for source_name, rows in datasets.items():
            for row in rows:
                key_val = row.get(key_column)
                if key_val is None:
                    result.warnings.append(f"Linha sem chave '{key_column}' ignorada em '{source_name}'")
                    continue
                if key_val not in seen_keys:
                    seen_keys.add(key_val)
                    row["_source"] = source_name
                    result.merged_rows.append(row)
                    result.source_counts[source_name] += 1
                else:
                    result.warnings.append(f"Chave duplicada '{key_val}' em '{source_name}' ignorada")

        return result

    def aggregate(self, rows: list[dict], column: str, func: AggFunc) -> float | int:
        values = [r.get(column) for r in rows if r.get(column) is not None]
        numeric_vals = [v for v in values if isinstance(v, (int, float))]
        if not numeric_vals:
            return 0
        if func == AggFunc.SUM:
            return sum(numeric_vals)
        if func == AggFunc.AVG:
            return round(sum(numeric_vals) / len(numeric_vals), 2)
        if func == AggFunc.COUNT:
            return len(numeric_vals)
        if func == AggFunc.MIN:
            return min(numeric_vals)
        if func == AggFunc.MAX:
            return max(numeric_vals)
        return 0

    @property
    def registered_sources(self) -> list[str]:
        return sorted(self.sources.keys())
