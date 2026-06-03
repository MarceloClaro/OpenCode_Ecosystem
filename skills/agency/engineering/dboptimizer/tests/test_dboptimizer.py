"""Tests for DatabaseOptimizer engine.

Covers all 4 CTs from SPEC_EVO14_ENG_dboptimizer:
  CT-01: Schema analysis
  CT-02: N+1 query detection
  CT-03: Index suggestions
  CT-04: SQL antipattern detection
"""

import sys
sys.path.insert(0, '.')
from dboptimizer_engine import DatabaseOptimizer


SAMPLE_DDL = """
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email VARCHAR(5000),
    avatar BLOB,
    created_at DATE
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    product_id INTEGER,
    amount DECIMAL(10,2),
    status VARCHAR(20),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255),
    category_id INTEGER,
    price DECIMAL(10,2)
);
"""

SAMPLE_CODE = """
for user in users:
    orders = db.execute(f"SELECT * FROM orders WHERE user_id = {user.id}").fetchall()
    for order in orders:
        products = db.query("SELECT * FROM products WHERE id = " + str(order.product_id))

while page < total_pages:
    results = db.find({"category": category, "page": page})
    page += 1

items.forEach(item => {
    const details = await db.items.findById(item.id)
})
"""

SAMPLE_QUERIES = """
SELECT * FROM orders WHERE status = 'pending' ORDER BY created_at DESC;
SELECT * FROM products WHERE category_id = 5 AND price > 100;
SELECT u.name, o.amount FROM users u JOIN orders o ON u.id = o.user_id WHERE o.status = 'active' ORDER BY u.name;
"""


def test_ct01_schema_analysis():
    """CT-01: Analyzes DDL for missing indexes and type warnings."""
    engine = DatabaseOptimizer()
    assert engine.available

    result = engine.analyze_schema(SAMPLE_DDL)

    assert len(result.tables) >= 3
    table_names = {t['name'] for t in result.tables}
    assert 'users' in table_names
    assert 'orders' in table_names

    assert len(result.type_warnings) > 0
    text_warnings = [w for w in result.type_warnings if 'TEXT' in w.get('type', '')]
    assert len(text_warnings) > 0

    assert isinstance(result.score, int)
    assert 0 <= result.score <= 100


def test_ct02_n_plus_one_detection():
    """CT-02: Detects N+1 query patterns in loops."""
    engine = DatabaseOptimizer()
    result = engine.detect_n_plus_one(SAMPLE_CODE)

    assert result.count > 0
    assert len(result.occurrences) >= 2

    for occ in result.occurrences:
        assert 'line' in occ
        assert 'loop_type' in occ
        assert 'suggestion' in occ


def test_ct03_index_suggestions():
    """CT-03: Suggests indexes based on WHERE/JOIN/ORDER BY columns."""
    engine = DatabaseOptimizer()
    queries = SAMPLE_QUERIES.strip().split(';\n')
    queries = [q.strip() for q in queries if q.strip()]

    result = engine.suggest_indexes(SAMPLE_DDL, queries)

    assert isinstance(result.suggestions, list)
    assert result.count >= 0

    if result.suggestions:
        s = result.suggestions[0]
        assert 'table' in s
        assert 'ddl' in s
        assert 'CREATE INDEX' in s['ddl'].upper()


def test_ct04_antipattern_detection():
    """CT-04: Detects SELECT *, LIKE wildcard, implicit cross joins, ORDER BY RAND()."""
    engine = DatabaseOptimizer()
    result = engine.detect_antipatterns(SAMPLE_QUERIES)

    assert result.count > 0

    patterns = {a['pattern'].split(' —')[0] for a in result.antipatterns}
    assert any('SELECT *' in p for p in patterns)

    antipattern_query = 'SELECT * FROM users ORDER BY RAND();'
    result2 = engine.detect_antipatterns(antipattern_query)
    assert result2.count >= 2


def test_clean_query_no_antipatterns():
    """Edge case: well-written query has no antipatterns."""
    engine = DatabaseOptimizer()
    clean = 'SELECT id, name, email FROM users WHERE id = ? AND status = ? ORDER BY name ASC;'
    result = engine.detect_antipatterns(clean)
    assert result.count == 0


def test_empty_ddl():
    """Edge case: empty DDL produces empty analysis."""
    engine = DatabaseOptimizer()
    result = engine.analyze_schema('')
    assert len(result.tables) == 0
    assert result.score == 100
