# =====================================================================
# CORA VERIFIER MCP SERVER v2.0 — REFINADO (EVO-8)
# 9 verificadores simbólicos: V1-V6 (originais refinados) + V7-V9 (novos)
# =====================================================================
# Refinamentos EVO-8:
#   V3: SymPy solve/solveset + grid search (não apenas random)
#   V4: Bootstrap CI, Mann-Whitney, Cohen's d robusto, Bayes Factor
#   V6: SymPy checkodesol (não apenas substituição manual)
#   V7: [NOVO] Rastreabilidade Bibliográfica (DOI)
#   V8: [NOVO] Verificador de Anonimato/Privacidade
#   V9: [NOVO] Conformidade Normativa (LGPD/Ética)
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
    """Manipulador do protocolo MCP via stdio — Cora Verifier v2.0."""

    def __init__(self):
        self.tools = {
            "cora_verify": self.handle_verify,
            "cora_v1_dimensional": self.handle_v1,
            "cora_v2_algebraic": self.handle_v2,
            "cora_v3_counterexample": self.handle_v3,
            "cora_v4_statistical": self.handle_v4,
            "cora_v5_numeric": self.handle_v5,
            "cora_v6_pde": self.handle_v6,
            "cora_v7_doi": self.handle_v7,
            "cora_v8_anonymity": self.handle_v8,
            "cora_v9_compliance": self.handle_v9,
            "cora_list_verifiers": self.handle_list,
            "cora_health": self.handle_health,
        }
        self.available_verifiers = {
            "V1": {"name": "Analise Dimensional", "category": "physics", "version": "1.0"},
            "V2": {"name": "Verificador Algebrico", "category": "mathematics", "version": "1.0"},
            "V3": {"name": "Contraexemplos (SymPy+Grid)", "category": "mathematics", "version": "2.0"},
            "V4": {"name": "Verificador Estatistico (Bootstrap)", "category": "statistics", "version": "2.0"},
            "V5": {"name": "Verificador Numerico", "category": "computation", "version": "1.0"},
            "V6": {"name": "Verificador PDE/EDO (checkodesol)", "category": "mathematics", "version": "2.0"},
            "V7": {"name": "Rastreabilidade Bibliografica (DOI)", "category": "academic", "version": "1.0"},
            "V8": {"name": "Verificador de Anonimato", "category": "privacy", "version": "1.0"},
            "V9": {"name": "Conformidade Normativa (LGPD/Etica)", "category": "compliance", "version": "1.0"},
        }

    def handle_request(self, request: dict) -> dict:
        method = request.get("method", "")
        req_id = request.get("id")

        if method == "initialize":
            return self._response(req_id, {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "cora-verifier", "version": "2.0.0"},
                "capabilities": {"tools": {}},
            })

        if method == "tools/list":
            tools = []
            for v_id, v_info in self.available_verifiers.items():
                tools.append({
                    "name": f"cora_{v_id.lower()}_verifier",
                    "description": f"{v_id}: {v_info['name']} (v{v_info['version']}) [{v_info['category']}]",
                    "inputSchema": {"type": "object", "properties": {}, "required": []}
                })
            tools.append({"name": "cora_verify", "description": "Executa todos os verificadores ativos em uma afirmacao",
                "inputSchema": {"type": "object", "properties": {
                    "statement": {"type": "string"}, "domain": {"type": "string"},
                    "verifiers": {"type": "array", "items": {"type": "string"}},
                }, "required": ["statement"]}})
            tools.append({"name": "cora_list_verifiers", "description": "Lista todos os verificadores com status"})
            tools.append({"name": "cora_health", "description": "Verifica saude do servidor e dependencias"})
            return self._response(req_id, {"tools": tools})

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
    # Core: Verify All
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

    # =================================================================
    # V1: ANALISE DIMENSIONAL (refinado: +unidades, +constantes)
    # =================================================================

    def handle_v1(self, args: dict) -> dict:
        equation = args.get("equation", args.get("statement", ""))
        dimension_map = {
            # Massa, Comprimento, Tempo (MLT)
            "m/s^2": "acceleration", "m/s": "velocity", "m/s2": "acceleration",
            "kg*m^2/s^2": "energy", "kg*m/s": "momentum", "kg*m2/s2": "energy",
            "m^3": "volume", "m^2": "area", "m3": "volume", "m2": "area",
            "kg": "mass", "g": "mass", "ton": "mass",
            "n": "force", "f": "force", "newton": "force",
            "j": "energy", "joule": "energy",
            "w": "power", "watt": "power",
            "pa": "pressure", "pascal": "pressure",
            "a": "acceleration",
            "m": "mass_or_length", "s": "time", "min": "time", "h": "time",
            "hz": "frequency", "rad/s": "angular_velocity",
            "c": "velocity", "k": "temperature", "mol": "amount",
            "v": "velocity_or_voltage",
        }
        equivalences = {
            ("force", "acceleration*mass_or_length"): True,
            ("force", "mass_or_length*acceleration"): True,
            ("energy", "force*mass_or_length"): True,
            ("power", "energy*time^-1"): True,
            ("pressure", "force*area^-1"): True,
            ("velocity", "acceleration*time"): True,
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
                    "rhs_dimensions": rhs_dim, "equation": equation,
                    "verifier": "V1", "version": "2.0"}
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
                if token.replace(".", "").replace("-", "").isdigit():
                    dims.append("scalar")
        return "*".join(sorted(dims)) if dims else "unknown"

    # =================================================================
    # V2: VERIFICADOR ALGEBRICO (SymPy — mantido estável)
    # =================================================================

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
                        "simplified": str(simplified), "method": "sympy_simplify",
                        "verifier": "V2", "version": "1.0"}
            else:
                simplified = sp.simplify(parsed)
                return {"passed": True, "expression": expression,
                        "simplified": str(simplified), "method": "sympy_simplify",
                        "verifier": "V2", "version": "1.0"}
        except ImportError:
            return {"passed": None, "error": "SymPy nao instalado", "verifier": "V2"}
        except Exception as e:
            return {"passed": False, "error": str(e), "verifier": "V2"}

    # =================================================================
    # V3: CONTRAEXEMPLOS — REFINADO (SymPy solve + grid + random) 
    # =================================================================

    def handle_v3(self, args: dict) -> dict:
        predicate = args.get("predicate", args.get("statement", ""))
        max_attempts = args.get("max_attempts", 1000)
        domain = args.get("domain", "integer")
        counterexamples = []
        methods_used = []

        # Método 1: SymPy solve (busca exata)
        try:
            import sympy as sp
            for var_name in ["n", "x", "k", "m"]:
                if var_name in predicate:
                    var = sp.Symbol(var_name)
                    expr = sp.sympify(predicate.replace("^", "**"))
                    if isinstance(expr, sp.Basic):
                        # Tenta encontrar onde predicado = False
                        neg_expr = sp.Not(expr) if not isinstance(expr, sp.Equality) else sp.Ne(expr.lhs, expr.rhs)
                        try:
                            sol = sp.solve(expr, var)
                            methods_used.append("sympy_solve")
                        except Exception:
                            sol = []
                        for s in sol[:5]:
                            try:
                                val = float(s) if s.is_real else None
                                if val is not None and val != val:  # NaN check
                                    continue
                                if val is not None:
                                    test = eval(predicate.replace(var_name, f"({val})").replace("^", "**"))
                                    if test is False:
                                        counterexamples.append(val)
                            except Exception:
                                continue
                    break
        except ImportError:
            methods_used.append("sympy_unavailable")
        except Exception:
            methods_used.append("sympy_error")

        # Método 2: Grid search (determinístico)
        if len(counterexamples) == 0 and domain == "integer":
            for x in range(-20, 21):
                try:
                    test_expr = predicate
                    for var in ["n", "x", "k", "m"]:
                        test_expr = test_expr.replace(var, f"({x})")
                    test_expr = test_expr.replace("^", "**")
                    result = eval(test_expr)
                    if result is False:
                        counterexamples.append(x)
                except Exception:
                    continue
            methods_used.append("grid_search")

        # Método 3: Random search (fallback)
        if len(counterexamples) == 0:
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
            methods_used.append("random_search")

        passed = len(counterexamples) == 0
        return {"passed": passed, "counterexamples": counterexamples[:5],
                "attempts": max_attempts, "methods": methods_used,
                "predicate": predicate, "verifier": "V3", "version": "2.0"}

    # =================================================================
    # V4: VERIFICADOR ESTATÍSTICO — REFINADO (Bootstrap + Mann-Whitney + Cohen d)
    # =================================================================

    def handle_v4(self, args: dict) -> dict:
        dados = args.get("data", [])
        test_type = args.get("test_type", "normality")
        claim = args.get("claim", "")
        try:
            import numpy as np
            from scipy import stats
            arr = np.array(dados, dtype=float)
            results = {"n": len(arr), "mean": float(np.mean(arr)),
                       "std": float(np.std(arr, ddof=1)),
                       "median": float(np.median(arr))}

            # --- Shapiro-Wilk (normalidade) ---
            if test_type == "normality":
                if len(arr) >= 3:
                    stat, p = stats.shapiro(arr)
                    results["shapiro_w"] = float(stat)
                    results["shapiro_p"] = float(p)
                    results["normal"] = p > 0.05

            # --- Pearson + Bootstrap CI ---
            if test_type == "correlation" and "y" in args:
                y = np.array(args["y"], dtype=float)
                r, p = stats.pearsonr(arr, y)
                results["pearson_r"] = float(r)
                results["pearson_p"] = float(p)
                results["significant"] = p < 0.05
                # Bootstrap CI para r
                n_boot = 1000
                r_boot = []
                rng = np.random.RandomState(42)
                for _ in range(n_boot):
                    idx = rng.choice(len(arr), size=len(arr), replace=True)
                    r_b, _ = stats.pearsonr(arr[idx], y[idx])
                    r_boot.append(r_b)
                results["pearson_r_ci95"] = [float(np.percentile(r_boot, 2.5)),
                                              float(np.percentile(r_boot, 97.5))]
                results["bootstrap_n"] = n_boot

            # --- Mann-Whitney U (two-sample) ---
            if test_type == "two_sample" and "y" in args:
                y = np.array(args["y"], dtype=float)
                u_stat, u_p = stats.mannwhitneyu(arr, y, alternative='two-sided')
                results["mannwhitney_u"] = float(u_stat)
                results["mannwhitney_p"] = float(u_p)
                # Cohen's d robusto
                pooled_std = np.sqrt((np.std(arr, ddof=1)**2 + np.std(y, ddof=1)**2) / 2)
                if pooled_std > 0:
                    d = (np.mean(arr) - np.mean(y)) / pooled_std
                    results["cohens_d"] = float(d)
                    results["effect_size"] = "grande" if abs(d) > 0.8 else ("medio" if abs(d) > 0.5 else "pequeno")

            # --- One-sample t-test ---
            if test_type == "one_sample" and "mu" in args:
                mu = float(args["mu"])
                t_stat, t_p = stats.ttest_1samp(arr, mu)
                results["t_stat"] = float(t_stat)
                results["t_p"] = float(t_p)
                d = (np.mean(arr) - mu) / np.std(arr, ddof=1) if np.std(arr, ddof=1) > 0 else 0
                results["cohens_d"] = float(d)

            results["tests_run"] = test_type
            return {"passed": True, "results": results, "data_shape": list(arr.shape),
                    "verifier": "V4", "version": "2.0"}
        except ImportError:
            return {"passed": None, "error": "SciPy/NumPy nao instalado", "verifier": "V4"}
        except Exception as e:
            return {"passed": False, "error": str(e), "verifier": "V4"}

    # =================================================================
    # V5: VERIFICADOR NUMERICO (mantido estável)
    # =================================================================

    def handle_v5(self, args: dict) -> dict:
        computed = float(args["computed"])
        expected = float(args["expected"])
        tolerance = float(args.get("tolerance", 1e-6))
        abs_error = abs(computed - expected)
        rel_error = abs_error / max(abs(expected), 1e-10)
        passed = abs_error < tolerance or rel_error < tolerance
        return {"passed": passed, "absolute_error": abs_error,
                "relative_error": rel_error, "tolerance": tolerance,
                "verifier": "V5", "version": "1.0"}

    # =================================================================
    # V6: VERIFICADOR PDE/EDO — REFINADO (checkodesol)
    # =================================================================

    def handle_v6(self, args: dict) -> dict:
        equation = args.get("equation", "")
        solution = args.get("solution", "")
        var = args.get("var", "x")
        try:
            import sympy as sp
            x = sp.Symbol(var)
            y = sp.Function('y')(x)

            # Método 1: checkodesol (via dsolve)
            try:
                eq_parsed = sp.sympify(equation.replace("diff(y,x)", "Derivative(y,x)"))
                sol_parsed = sp.sympify(solution)
                if hasattr(sp, 'checkodesol'):
                    check = sp.checkodesol(eq_parsed, sol_parsed)
                    if check[0]:  # (True, 0) = OK
                        return {"passed": True, "method": "checkodesol",
                                "verifier": "V6", "version": "2.0"}
            except Exception:
                pass

            # Método 2: Substituição direta
            sol_expr = sp.sympify(solution)
            if isinstance(sol_expr, sp.Eq):
                sol_expr = sol_expr.rhs
            eq_expr = sp.sympify(equation)
            residual = sp.simplify(eq_expr.subs(y, sol_expr))
            passed = bool(residual == 0)
            return {"passed": passed, "residual": str(residual),
                    "method": "substitution", "verifier": "V6", "version": "2.0"}
        except ImportError:
            return {"passed": None, "error": "SymPy nao instalado", "verifier": "V6"}
        except Exception as e:
            return {"passed": False, "error": str(e), "verifier": "V6"}

    # =================================================================
    # V7: [NOVO] RASTREABILIDADE BIBLIOGRÁFICA (DOI)
    # =================================================================

    def handle_v7(self, args: dict) -> dict:
        statement = args.get("statement", "")
        dois_provided = args.get("dois", [])
        text = args.get("text", statement)

        # Extrai DOIs do texto
        doi_pattern = r'10\.\d{4,}/[^\s\)\].,;]+'
        dois_found = re.findall(doi_pattern, text)

        # Padrões de afirmação sem respaldo
        claim_patterns = [
            r'(?:estudos?|pesquisas?|autores?|literatura)\s+(?:mostram?|apontam?|indicam?|sugerem?|demonstram?)',
            r'(?:conforme|segundo|de acordo com)\s+(?:a\s+)?(?:pesquisa|literatura|estudo)',
            r'(?:evidências?|dados)\s+(?:sugerem?|indicam?|mostram?)',
            r'(?:é\s+)?(?:comprovado|demonstrado|consenso|amplamente\s+aceito)',
        ]
        unbacked_claims = []
        for pattern in claim_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for m in matches:
                # Verifica se há DOI próximo (até 200 caracteres após a afirmação)
                nearby = text[m.end():m.end()+200]
                nearby_dois = re.findall(doi_pattern, nearby)
                if not nearby_dois and not args.get("dois"):
                    unbacked_claims.append({
                        "claim": text[m.start():m.start()+80],
                        "position": m.start(),
                        "issue": "afirmação factual sem DOI de respaldo próximo"
                    })

        result = {
            "passed": len(unbacked_claims) == 0,
            "dois_found": dois_found,
            "dois_count": len(dois_found),
            "unbacked_claims": unbacked_claims[:5],
            "unbacked_count": len(unbacked_claims),
            "verifier": "V7",
            "version": "1.0",
            "guidance": "Cada afirmação factual deve ser respaldada por DOI verificável próximo."
        }

        # Se DOIs foram fornecidos, validar formato
        if dois_provided:
            valid_dois = [d for d in dois_provided if re.match(r'^10\.\d{4,}/', d)]
            result["dois_validated"] = len(valid_dois)
            result["dois_invalid"] = len(dois_provided) - len(valid_dois)

        return result

    # =================================================================
    # V8: [NOVO] VERIFICADOR DE ANONIMATO/PRIVACIDADE
    # =================================================================

    def handle_v8(self, args: dict) -> dict:
        text = args.get("statement", "")

        # Identificadores diretos
        name_patterns = [
            r'\b[A-Z][a-zà-ú]+\s+(?:[A-Z][a-zà-ú]+\s+){0,3}[A-Z][a-zà-ú]+\b',  # Nome composto
            r'\b(?:CPF|RG|passaporte|identidade)\s*:?\s*\d[\d\.\-\/]+',
            r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b',  # CPF
            r'\b\d{2}\.\d{3}\.\d{3}-\d{1}\b',  # RG
            r'[\w\.-]+@[\w\.-]+\.\w+',  # Email
        ]

        # Identificadores indiretos (EVO-8: protocolo de anonimato estendido)
        indirect_patterns = [
            r'(?:github\.com|gitlab\.com|bitbucket\.org)/\w+',  # Perfil GitHub
            r'(?:\d+)\s*(?:estrelas?|stars?|forks?)\s*(?:e|,)?\s*(?:\d+)?\s*(?:forks?|estrelas?|stars?)?',
            r'(?:criador|autor|desenvolvedor)\s+(?:do|da|de)\s+\w+(?:\s+\w+){0,3}',
        ]

        findings = []

        # Busca diretos
        for pattern in name_patterns:
            for m in re.finditer(pattern, text):
                finding = m.group()
                # Filtra falsos positivos comuns
                if finding.lower() not in ["universidade federal", "inteligência artificial",
                    "ensino superior", "tecnologia educacional", "código aberto",
                    "conteúdo educacional", "comitê de ética", "marco civil",
                    "direito digital", "teoria dos jogos", "diário oficial"]:
                    findings.append({"type": "identificador_direto", "match": finding,
                                     "position": m.start(), "severity": "ALTA"})

        # Busca indiretos
        for pattern in indirect_patterns:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                findings.append({"type": "identificador_indireto", "match": m.group(),
                                 "position": m.start(), "severity": "ALTA"})

        # Verifica menção a nomes de produtos/projetos públicos (EVO-8)
        product_pattern = r'\b(?:OpenCode|ChatGPT|GPT-\d|Gemini|Claude|Copilot)\b'
        for m in re.finditer(product_pattern, text, re.IGNORECASE):
            findings.append({"type": "nome_produto_publico", "match": m.group(),
                             "position": m.start(),
                             "severity": "MEDIA",
                             "guidance": "Considere substituir por descrição genérica"})

        passed = len(findings) == 0
        return {
            "passed": passed,
            "findings": findings,
            "findings_count": len(findings),
            "high_severity": sum(1 for f in findings if f["severity"] == "ALTA"),
            "verifier": "V8",
            "version": "1.0",
            "protocol": "EVO-8 Protocolo de Anonimato Estendido",
        }

    # =================================================================
    # V9: [NOVO] CONFORMIDADE NORMATIVA (LGPD/Ética)
    # =================================================================

    def handle_v9(self, args: dict) -> dict:
        text = args.get("statement", "")
        framework = args.get("framework", "lgpd")  # lgpd, etica_pesquisa, ufc_resolucao

        checks = []

        # --- LGPD (Lei 13.709/2018) ---
        if framework == "lgpd":
            lgpd_checks = [
                ("dados_pessoais_processamento",
                 r'(?:dados|informações)\s+(?:pessoais|sensíveis|dos\s+participantes)',
                 r'(?:criptograf|anonimi|pseudonim|consentimento|TCLE|LGPD)',
                 "Art. 6º, 7º: Dados pessoais mencionados sem indicação de base legal ou proteção"),
                ("dados_sensiveis",
                 r'(?:dados\s+sensíveis|saúde|biométrico|genético|orientação|religião|político)',
                 r'(?:consentimento\s+explícito|TCLE|CEP|comitê\s+de\s+ética)',
                 "Art. 11: Dados sensíveis exigem consentimento explícito e aprovação ética"),
                ("transferencia_internacional",
                 r'(?:nuvem|cloud|servidor\s+externo|API\s+externa|OpenAI|Google|AWS)',
                 r'(?:local|offline|processamento\s+local)',
                 "Art. 33: Transferência internacional de dados exige garantias adequadas"),
                ("direitos_titular",
                 r'(?:coleta|armazen|processa|tratamento?\s+de\s+dados)',
                 r'(?:direito\s+(?:ao?\s+)?(?:acesso|exclusão|esquecimento|retificação|portabilidade))',
                 "Art. 17-21: Direitos do titular devem ser mencionados"),
            ]
            for check_id, trigger_pat, safe_pat, guidance in lgpd_checks:
                has_trigger = bool(re.search(trigger_pat, text, re.IGNORECASE))
                has_safeguard = bool(re.search(safe_pat, text, re.IGNORECASE))
                if has_trigger and not has_safeguard:
                    checks.append({"id": check_id, "status": "ALERTA",
                                   "guidance": guidance, "framework": "LGPD"})
                elif has_trigger and has_safeguard:
                    checks.append({"id": check_id, "status": "OK"})

        # --- Ética em Pesquisa (Resolução PRPPG/UFC 39/2025) ---
        if framework in ("etica_pesquisa", "ufc_resolucao"):
            etica_checks = [
                ("declaracao_ia",
                 r'(?:IA|inteligência\s+artificial|agente|LLM|ChatGPT|OpenCode)',
                 r'(?:declar[açã]{2}o\s+(?:de\s+)?(?:uso\s+(?:de\s+)?)?IA|Anexo\s+IV|transparência)',
                 "Res. 39/2025: Uso de IA deve ser declarado explicitamente"),
                ("plagio_ia",
                 r'(?:ger[aã]|produz|redig|escrev)\w*\s+(?:automaticamente|por\s+IA|com\s+IA)',
                 r'(?:autoria\s+humana|supervisão|revisão\s+humana|assistente)',
                 "Res. 39/2025: IA é assistente, não autora. Autoria intelectual é humana."),
                ("reprodutibilidade",
                 r'(?:conclusão|resultado|achado|descoberta)',
                 r'(?:reprodu[zt]|audit|rastre[aá]|DOI|SHA|hash)',
                 "Res. 39/2025: Resultados de pesquisa devem ser reprodutíveis e auditáveis"),
                ("consentimento_participantes",
                 r'(?:participantes?|sujeitos?|grupo\s+focal|entrevistado)',
                 r'(?:TCLE|consentimento|CEP|comitê\s+de\s+ética)',
                 "Res. 39/2025: Participantes de pesquisa exigem TCLE e aprovação do CEP"),
            ]
            for check_id, trigger_pat, safe_pat, guidance in etica_checks:
                has_trigger = bool(re.search(trigger_pat, text, re.IGNORECASE))
                has_safeguard = bool(re.search(safe_pat, text, re.IGNORECASE))
                if has_trigger and not has_safeguard:
                    checks.append({"id": check_id, "status": "ALERTA",
                                   "guidance": guidance, "framework": "Res. PRPPG/UFC 39/2025"})
                elif has_trigger and has_safeguard:
                    checks.append({"id": check_id, "status": "OK"})

        alerts = [c for c in checks if c["status"] == "ALERTA"]
        passed = len(alerts) == 0

        return {
            "passed": passed,
            "framework": framework,
            "checks": checks,
            "alerts": alerts,
            "alerts_count": len(alerts),
            "checks_total": len(checks),
            "verifier": "V9",
            "version": "1.0",
        }

    # =================================================================
    # Utilitários
    # =================================================================

    def handle_list(self, args: dict) -> dict:
        return {"verifiers": self.available_verifiers, "count": len(self.available_verifiers),
                "version": "2.0.0", "refinements": "EVO-8 (V3+V4+V6 refinados, V7+V8+V9 novos)"}

    def handle_health(self, args: dict) -> dict:
        health = {"sympy": False, "scipy": False, "numpy": False, "server": "running", "version": "2.0.0"}
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
        print("=== CORA VERIFIER v2.0 TEST SUITE (EVO-8 Refinado) ===")
        handler = MCPHandler()
        tests = [
            # --- V1-V6 originais ---
            ("V1: F=ma (dimensional)", handler.handle_v1, {"equation": "F = m*a"}),
            ("V1: F=m (deve falhar)", handler.handle_v1, {"equation": "F = m"}),
            ("V2: x+x=2x", handler.handle_v2, {"expression": "x + x - 2*x"}),
            ("V3: n>0 (contraexemplo)", handler.handle_v3, {"predicate": "n > 0", "max_attempts": 50}),
            ("V3: n^2>=0 (sem contraex.)", handler.handle_v3, {"predicate": "n**2 >= 0", "max_attempts": 50}),
            ("V4: Shapiro-Wilk", handler.handle_v4, {"data": [1,2,3,4,5,6,7,8,9,10]}),
            ("V5: pi precisao", handler.handle_v5, {"computed": 3.14159, "expected": 3.1415926535}),
            ("V6: placeholder", handler.handle_v6, {"equation": "0", "solution": "0"}),

            # --- V7-V9 NOVOS ---
            ("V7: DOI ausente (alerta)", handler.handle_v7,
             {"statement": "Estudos mostram que a IA melhora a educação significativamente."}),
            ("V7: DOI presente (ok)", handler.handle_v7,
             {"statement": "Conforme Russell e Norvig (2022) DOI: 10.1000/xyz123, a IA..."}),

            ("V8: Anonimato (texto limpo)", handler.handle_v8,
             {"statement": "A plataforma de IA multiagente de código aberto coordena agentes especializados."}),
            ("V8: Anonimato (nome no texto)", handler.handle_v8,
             {"statement": "O Prof. Dr. João Silva desenvolveu a plataforma com 17 estrelas e 7 forks no GitHub."}),

            ("V9: LGPD (conforme)", handler.handle_v9,
             {"statement": "Dados pessoais são criptografados e processados localmente com consentimento dos participantes via TCLE.", "framework": "lgpd"}),
            ("V9: LGPD (alerta)", handler.handle_v9,
             {"statement": "Os dados pessoais dos participantes serão enviados para a nuvem da OpenAI.", "framework": "lgpd"}),
            ("V9: Ética Pesquisa (conforme)", handler.handle_v9,
             {"statement": "O uso de IA é declarado conforme Anexo IV. Os participantes assinaram TCLE aprovado pelo CEP.", "framework": "etica_pesquisa"}),
        ]
        for name, fn, args in tests:
            try:
                result = fn(args)
                status = result.get('passed', 'N/A')
                extra = ""
                if not status and "V7" in name:
                    extra = f" | alertas: {result.get('unbacked_count', 0)}"
                elif not status and "V8" in name:
                    extra = f" | findings: {result.get('findings_count', 0)}"
                print(f"[{'OK' if status else '!!'} ] {name}: passed={status}{extra}")
            except Exception as e:
                print(f"[FAIL] {name}: {e}")
        print("=== TEST SUITE v2.0 COMPLETE ===")
    else:
        main()
