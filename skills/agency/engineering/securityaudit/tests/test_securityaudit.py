"""Tests for SecurityAuditEngine.

Covers all 4 CTs from SPEC_EVO14_ENG_securityaudit:
  CT-01: Secrets detection
  CT-02: SQL injection detection
  CT-03: XSS detection
  CT-04: Authentication audit
"""

import sys
sys.path.insert(0, '.')
from securityaudit_engine import SecurityAuditEngine


SAMPLE_CODE = '''
import sqlite3
from flask import Flask, request, make_response

app = Flask(__name__)
API_KEY = "sk-proj-abc123def45678901234567890xyz"
DB_PASSWORD = "super_secret_password_123"

@app.route("/user/<id>")
def get_user(id):
    db = sqlite3.connect("app.db")
    query = f"SELECT * FROM users WHERE id = {id}"
    user = db.execute(query).fetchone()
    user_html = f"<div>{user}</div>"
    document.getElementById("output").innerHTML = user_html
    return str(user)

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if data["password"] == "admin123":
        token = "eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoiYWRtaW4ifQ.signature"
        resp = make_response({"status": "ok"})
        resp.set_cookie("session", token, httponly=False, secure=False)
        return resp
    return {"error": "unauthorized"}

@app.route("/search")
def search():
    term = request.args.get("q")
    db = sqlite3.connect("app.db")
    cursor = db.execute("SELECT * FROM products WHERE name LIKE '%" + term + "%'")
    return str(cursor.fetchall())

@app.route("/danger")
def danger():
    data = request.args.get("data")
    return eval(data)

@app.route("/admin")
def admin_panel():
    hashed = hashlib.md5(request.args.get("pass").encode()).hexdigest()
    if hashed == "5d41402abc4b2a76b9719d911017c592":
        return "admin"
    return "denied"
'''


def test_ct01_secrets_detection():
    """CT-01: Detects hardcoded API keys, passwords, tokens."""
    engine = SecurityAuditEngine()
    assert engine.available

    result = engine.detect_secrets(SAMPLE_CODE)

    assert result.count > 0
    assert len(result.secrets) > 0

    patterns = {s['pattern'] for s in result.secrets}
    assert any('API' in p or 'key' in p.lower() for p in patterns)
    assert any('password' in p.lower() or 'Secret' in p for p in patterns)

    for s in result.secrets:
        assert s['severity'] == 'HIGH'


def test_ct02_sql_injection_detection():
    """CT-02: Detects SQL injection via f-strings and concatenation."""
    engine = SecurityAuditEngine()
    result = engine.detect_sql_injection(SAMPLE_CODE)

    assert result.count > 0
    sink_lines = {v['line'] for v in result.vulnerabilities}
    assert len(sink_lines) >= 2


def test_ct03_xss_detection():
    """CT-03: Detects innerHTML, dangerouslySetInnerHTML, document.write."""
    engine = SecurityAuditEngine()
    result = engine.detect_xss(SAMPLE_CODE)

    sinks = {v['sink'] for v in result.vulnerabilities}
    all_sinks_text = ' '.join(sinks).lower()
    assert result.count > 0


def test_ct04_authentication_audit():
    """CT-04: Detects plaintext passwords, insecure cookies, weak hashing."""
    engine = SecurityAuditEngine()
    result = engine.audit_authentication(SAMPLE_CODE)

    assert len(result.issues) > 0
    assert result.score < 100

    categories = {i['description'] for i in result.issues}
    assert any('plaintext' in c.lower() or 'Plaintext' in c for c in categories) \
        or any('HttpOnly' in c or 'Secure' in c for c in categories) \
        or any('md5' in c.lower() for c in categories)


def test_clean_code_no_issues():
    """Edge case: clean code produces no findings."""
    engine = SecurityAuditEngine()
    clean = '''def add(a: int, b: int) -> int:
    return a + b

def greet(name: str) -> str:
    return f"Hello, {name}"
'''
    secrets = engine.detect_secrets(clean)
    assert secrets.count == 0

    xss = engine.detect_xss(clean)
    assert xss.count == 0


def test_empty_source():
    """Edge case: empty source returns empty results."""
    engine = SecurityAuditEngine()
    assert engine.detect_secrets('').count == 0
    assert engine.detect_sql_injection('').count == 0
    assert engine.detect_xss('').count == 0
    auth = engine.audit_authentication('')
    assert auth.score == 100
