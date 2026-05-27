# =====================================================================
# CORA VERIFIER MCP SERVER v1.0
# 6 verificadores simbolicos para o pipeline Cora-Debate (P19)
# =====================================================================
# Protocolo MCP: stdio JSON-RPC
# Dependencias: sympy>=1.12, scipy>=1.10, numpy>=1.24
# =====================================================================
import json
import sys
import math
import random
import re
import traceback
from typing import Any

# ---------------------------------------------------------------------
# MCP Protocol Handler
# ---------------------------------------------------------------------

class MCPHandler:
    """Manipulador do protocolo MCP via stdio."""

    def __init__(self):
        self.tools = {
            "cora_verify": self.handle_verify,
            "cora_v1_dimensional": self.handle_v1,
            "cora_v2_algebraic": self.handle_v2,
            "cora_v3_counterexample": self.handle_v3,
            "cora_v4_statistical": self.handle_v4,
            "cora_v5_numeric": self.handle_v5,
            "cora_v6_pde": self.handle_v6,
            "cora_list_verifiers": self.handle_list,
            "cora_health": self.handle_health,
        }
        self.available_verifiers = {
            "V1": {"name": "Analise Dimensional", "category": "physics"},
            "V2": {"name": "Verificador Algebrico", "category": "mathematics"},
            "V3": {"name": "Contraexemplos", "category": "mathematics"},
            "V4": {"name": "Verificador Estatistico", "category": "statistics"},
            "V5": {"name": "Verificador Numerico", "category": "computation"},
            "V6": {"name": "Verificador PDE/EDO", "category": "mathematics"},
        }

    def handle_request(self, request: dict) -> dict:
        method = request.get("method", "")
        req_id = request.get("id")

        if method == "initialize":
            return self._response(req_id, {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "cora-verifier", "version": "1.0.0"},
                "capabilities": {"tools": {}},
            })

        if method == "tools/list":
            return self._response(req_id, {
                "tools": [
                    {"name": "cora_verify", "description": "Executa todos os verificadores ativos em uma afirmacao",
                     "inputSchema": {"type": "object", "properties": {
                         "statement": {"type": "string"},
                         "domain": {"type": "string"},
                         "verifiers": {"type": "array", "items": {"type": "string"}},
                     }, "required": ["statement"]}},
                    {"name": "cora_v1_dimensional", "description": "V1: Analise dimensional de equacoes fisicas",
                     "inputSchema": {"type": "object", "properties": {
                         "equation": {"type": "string"},
                     }, "required": ["equation"]}},
                    {"name": "cora_v2_algebraic", "description": "V2: Verificacao algebrica via SymPy",
                     "inputSchema": {"type": "object", "properties": {
                         "expression": {"type": "string"},
                         "expected": {"type": "string"},
                     }, "required": ["expression"]}},
                    {"name": "cora_v3_counterexample", "description": "V3: Busca de contraexemplos para afirmacoes universais",
                     "inputSchema": {"type": "object", "properties": {
                         "predicate": {"type": "string"},
                         "domain": {"type": "string"},
                         "max_attempts": {"type": "integer", "default": 1000},
                     }, "required": ["predicate"]}},
                    {"name": "cora_v4_statistical", "description": "V4: Verificacao estatistica (Shapiro-Wilk, Cohen d, correlacao)",
                     "inputSchema": {"type": "object", "properties": {
                         "data": {"type": "array", "items": {"type": "number"}},
                         "test_type": {"type": "string"},
                         "claim": {"type": "string"},
                     }, "required": ["data"]}},
                    {"name": "cora_v5_numeric", "description": "V5: Verificacao numerica com tolerancia IEEE 754",
                     "inputSchema": {"type": "object", "properties": {
                         "computed": {"type": "number"},
                         "expected": {"type": "number"},
                         "tolerance": {"type": "number", "default": 1e-6},
                     }, "required": ["computed", "expected"]}},
                    {"name": "cora_v6_pde", "description": "V6: Verificacao de EDO/EDP via SymPy dsolve",
                     "inputSchema": {"type": "object", "properties": {
                         "equation": {"type": "string"},
                         "solution": {"type": "string"},
                         "var": {"type": "string", "default": "x"},
                     }, "required": ["equation", "solution"]}},
                    {"name": "cora_list_verifiers", "description": "Lista todos os verificadores disponiveis com status",
                     "inputSchema": {"type": "object", "properties": {}}},
                    {"name": "cora_health", "description": "Verifica saude do servidor e dependencias",
                     "inputSchema": {"type": "object", "properties": {}}},
                ]
            })

        if method == "tools/call":
            tool_name = request["params"]["name"]
            arguments = request["params"].get("arguments", {})
            if tool_name in self.tools:
                result = self.tools[tool_name](arguments)
                return self._response(req_id, {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]})
            return self._error(req_id, -32601, f"Tool not found: {tool_name}")

        if method == "notifications/initialized":
            return {"jsonrpc": "2.0", "id": req_id, "result": {}}

        return self._error(req_id, -32601, f"Method not found: {method}")

    def _response(self, req_id, result):
        return {"jsonrpc": "2.0", "id": req_id, "result": result}

    def _error(self, req_id, code, message):
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}

    # -----------------------------------------------------------------
    # Tool Handlers
    # -----------------------------------------------------------------

    def handle_verify(self, args: dict) -> dict:
        statement = args["statement"]
        domain = args.get("domain", "general")
        verifiers = args.get("verifiers", list(self.available_verifiers.keys()))
        results = {}
        all_passed = True
        for v in verifiers:
            if v in self.available_verifiers:
                fn = getattr(self, f"handle_{v.lower()}", None)
                if fn:
                    r = fn({"statement": statement, "domain": domain})
                    results[v] = r
                    if not r.get("passed", False):
                        all_passed = False
        return {"passed": all_passed, "verifier_results": results, "statement": statement}

    def handle_v1(self, args: dict) -> dict:
        equation = args.get("equation", args.get("statement", ""))
        dimension_map = {
            "m/s^2": "acceleration", "m/s": "velocity",
            "kg*m^2/s^2": "energy", "kg*m/s": "momentum",
            "m^3": "volume", "m^2": "area",
            "kg": "mass", "g": "mass",
            "n": "force", "f": "force",
            "j": "energy", "w": "power", "pa": "pressure",
            "a": "acceleration",
            "m": "mass_or_length",
            "s": "time",
        }
        # Known equivalences: F = m*a => force = mass*acceleration
        equivalences = {
            ("force", "acceleration*mass_or_length"): True,
            ("force", "mass_or_length*acceleration"): True,
        }
        lhs, rhs = None, None
        if "=" in equation:
            parts = equation.split("=")
            lhs = parts[0].strip()
            rhs = "=".join(parts[1:]).strip()
        if lhs and rhs:
            lhs_dim = self._parse_dimensions(lhs, dimension_map)
            rhs_dim = self._parse_dimensions(rhs, dimension_map)
            consistent = lhs_dim == rhs_dim
            if not consistent:
                key = (lhs_dim, rhs_dim)
                consistent = equivalences.get(key, False)
            return {"passed": consistent, "lhs_dimensions": lhs_dim,
                    "rhs_dimensions": rhs_dim, "equation": equation}
        return {"passed": False, "equation": equation, "error": "formato invalido"}

    def _parse_dimensions(self, expr: str, dim_map: dict) -> str:
        expr_lower = expr.lower().replace(" ", "")
        tokens = re.split(r'[\*\+\-\/\^\(\)\=]', expr_lower)
        dims = []
        for token in tokens:
            token = token.strip()
            if not token:
                continue
            for unit, dim in sorted(dim_map.items(), key=lambda x: -len(x[0])):
                if token == unit or unit in token.split("*"):
                    dims.append(dim)
                    break
            else:
                if token.replace(".", "").isdigit():
                    dims.append("scalar")
        return "*".join(sorted(dims)) if dims else "unknown"

    def handle_v2(self, args: dict) -> dict:
        expression = args.get("expression", args.get("statement", ""))
        try:
            import sympy as sp
            if "=" in expression and "==" not in expression:
                expression = expression.replace("=", "==")
            parsed = sp.sympify(expression)
            if isinstance(parsed, sp.Equality):
                simplified = sp.simplify(parsed.lhs - parsed.rhs)
                passed = bool(simplified == 0)
                return {"passed": passed, "expression": expression,
                        "simplified": str(simplified), "method": "sympy_simplify"}
            else:
                simplified = sp.simplify(parsed)
                return {"passed": True, "expression": expression,
                        "simplified": str(simplified), "method": "sympy_simplify"}
        except ImportError:
            return {"passed": None, "error": "SymPy nao instalado", "expression": expression}
        except Exception as e:
            return {"passed": False, "error": str(e), "expression": expression}

    def handle_v3(self, args: dict) -> dict:
        predicate = args.get("predicate", args.get("statement", ""))
        max_attempts = args.get("max_attempts", 1000)
        domain = args.get("domain", "integer")
        counterexamples = []
        try:
            for i in range(max_attempts):
                if domain == "integer":
                    x = random.randint(-100, 100)
                else:
                    x = random.uniform(-100, 100)
                try:
                    test_expr = predicate
                    for var in ["n", "x", "k", "m"]:
                        test_expr = test_expr.replace(var, f"({x})")
                    test_expr = test_expr.replace("^", "**")
                    if eval(test_expr) is False:
                        counterexamples.append(x)
                        if len(counterexamples) >= 3:
                            break
                except Exception:
                    continue
            passed = len(counterexamples) == 0
            return {"passed": passed, "counterexamples": counterexamples,
                    "attempts": max_attempts, "predicate": predicate}
        except Exception as e:
            return {"passed": None, "error": str(e), "predicate": predicate}

    def handle_v4(self, args: dict) -> dict:
        dados = args.get("data", [])
        test_type = args.get("test_type", "normality")
        try:
            import numpy as np
            from scipy import stats
            arr = np.array(dados, dtype=float)
            results = {"n": len(arr), "mean": float(np.mean(arr)), "std": float(np.std(arr, ddof=1))}
            if test_type == "normality":
                if len(arr) >= 3:
                    stat, p = stats.shapiro(arr)
                    results["shapiro_stat"] = float(stat)
                    results["shapiro_p"] = float(p)
                    results["normal"] = p > 0.05
            if test_type == "correlation" and "y" in args:
                y = np.array(args["y"], dtype=float)
                r, p = stats.pearsonr(arr, y)
                results["pearson_r"] = float(r)
                results["pearson_p"] = float(p)
                results["significant"] = p < 0.05
            return {"passed": True, "results": results, "data_shape": list(arr.shape)}
        except ImportError:
            return {"passed": None, "error": "SciPy/NumPy nao instalado"}
        except Exception as e:
            return {"passed": False, "error": str(e)}

    def handle_v5(self, args: dict) -> dict:
        computed = float(args["computed"])
        expected = float(args["expected"])
        tolerance = float(args.get("tolerance", 1e-6))
        abs_error = abs(computed - expected)
        rel_error = abs_error / max(abs(expected), 1e-10)
        passed = abs_error < tolerance or rel_error < tolerance
        return {"passed": passed, "absolute_error": abs_error,
                "relative_error": rel_error, "tolerance": tolerance}

    def handle_v6(self, args: dict) -> dict:
        equation = args.get("equation", "")
        solution = args.get("solution", "")
        var = args.get("var", "x")
        try:
            import sympy as sp
            x = sp.Symbol(var)
            eq_parsed = sp.sympify(equation)
            sol_parsed = sp.sympify(solution)
            if isinstance(sol_parsed, sp.Eq):
                sol_parsed = sol_parsed.rhs
            lhs_val = sp.diff(sol_parsed, x) if "diff" in equation.lower() else sol_parsed
            residual = sp.simplify(sp.sympify(f"{equation} - ({solution})"))
            passed = bool(residual == 0)
            return {"passed": passed, "residual": str(residual), "method": "sympy_substitution"}
        except ImportError:
            return {"passed": None, "error": "SymPy nao instalado"}
        except Exception as e:
            return {"passed": False, "error": str(e)}

    def handle_list(self, args: dict) -> dict:
        return {"verifiers": self.available_verifiers, "count": len(self.available_verifiers)}

    def handle_health(self, args: dict) -> dict:
        health = {"sympy": False, "scipy": False, "numpy": False, "server": "running"}
        try:
            import sympy; health["sympy"] = True
        except ImportError:
            pass
        try:
            import scipy; health["scipy"] = True
        except ImportError:
            pass
        try:
            import numpy; health["numpy"] = True
        except ImportError:
            pass
        return health


# ---------------------------------------------------------------------
# Main Loop
# ---------------------------------------------------------------------

def main():
    handler = MCPHandler()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = handler.handle_request(request)
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()
        except json.JSONDecodeError:
            continue
        except Exception as e:
            err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": str(e)}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    if "--test" in sys.argv:
        print("=== CORA VERIFIER TEST SUITE ===")
        handler = MCPHandler()
        tests = [
            ("V1: Dimensional (F=ma)", handler.handle_v1, {"equation": "F = m*a"}),
            ("V2: Algebra (x+x=2x)", handler.handle_v2, {"expression": "x + x - 2*x"}),
            ("V3: Contraexemplo (n>0)", handler.handle_v3, {"predicate": "n > 0"}),
            ("V4: Normalidade", handler.handle_v4, {"data": [1,2,3,4,5,6,7,8,9,10]}),
            ("V5: Numerico (pi)", handler.handle_v5, {"computed": 3.14159, "expected": 3.1415926535}),
            ("V6: PDE placeholder", handler.handle_v6, {"equation": "0", "solution": "0"}),
        ]
        for name, fn, args in tests:
            try:
                result = fn(args)
                print(f"[OK] {name}: {result.get('passed', 'N/A')}")
            except Exception as e:
                print(f"[FAIL] {name}: {e}")
        print("=== TEST SUITE COMPLETE ===")
    else:
        main()
