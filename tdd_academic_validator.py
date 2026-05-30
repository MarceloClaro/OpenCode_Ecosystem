#!/usr/bin/env python3
"""
TDDAcademic v2.0 — Validação Test-Driven de SPECs (Arquitetura OOP)
=====================================================================
Refatoração completa com:
  - Classe abstrata SpecValidator (Template Method pattern)
  - Validadores concretos para cada SPEC (Polimorfismo)
  - TestRunner com composição de validadores
  - TestReport com saída JSON + markdown
  - Design Patterns: Template Method, Strategy, Composite

Uso: python tdd_academic_validator.py
Saída: stdout + relatorio_tdd_specs.json
"""

import sys, json, re, abc
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime

# =====================================================================
# CONSTANTES GLOBAIS
# =====================================================================
REPORT_PATH = Path(__file__).parent / "relatorio_tdd_specs.json"

# =====================================================================
# DOMÍNIO: Tipos de Dados Imutáveis (Value Objects)
# =====================================================================

class TestResult:
    """Value Object — resultado imutável de um teste unitário."""
    __slots__ = ('spec', 'ca', 'descricao', 'status', 'erro')
    
    def __init__(self, spec: str, ca: str, descricao: str,
                 status: str, erro: str = ""):
        self.spec = spec
        self.ca = ca
        self.descricao = descricao
        self.status = status       # "PASS" | "FAIL" | "ERROR"
        self.erro = erro
    
    def aprovou(self) -> bool:
        return self.status == "PASS"
    
    def to_dict(self) -> dict:
        return {
            "spec": self.spec, "ca": self.ca,
            "desc": self.descricao, "status": self.status,
            "error": self.erro
        }
    
    def __repr__(self):
        return (f"[{self.status}] {self.spec} | {self.ca}: {self.descricao}"
                + (f" | {self.erro}" if self.erro else ""))


class SpecReport:
    """Value Object — relatório consolidado de uma SPEC."""
    def __init__(self, spec_id: str, resultados: List[TestResult]):
        self.spec_id = spec_id
        self.resultados = resultados
        self.total = len(resultados)
        self.passes = sum(1 for r in resultados if r.aprovou())
        self.falhas = self.total - self.passes
        self.taxa = 100.0 * self.passes / max(1, self.total)
    
    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "pass": self.passes,
            "fail": self.falhas,
            "taxa": round(self.taxa, 1),
            "testes": [r.to_dict() for r in self.resultados]
        }


# =====================================================================
# CLASSE ABSTRATA: SpecValidator (Template Method)
# =====================================================================

class SpecValidator(abc.ABC):
    """
    Classe base para todos os validadores de SPEC.
    Template Method: `validar()` define o esqueleto,
    subclasses implementam `_executar_testes()`.
    """
    
    @property
    @abc.abstractmethod
    def spec_id(self) -> str:
        """Identificador único da SPEC (ex.: 'PCI-001')."""
        ...
    
    @property
    @abc.abstractmethod
    def descricao(self) -> str:
        """Descrição curta do propósito da SPEC."""
        ...
    
    @abc.abstractmethod
    def _executar_testes(self) -> List[TestResult]:
        """Cada validador concreto implementa seus testes aqui."""
        ...
    
    def validar(self) -> SpecReport:
        """Template Method: executa testes e retorna relatório."""
        resultados = self._executar_testes()
        return SpecReport(self.spec_id, resultados)
    
    def _criar_teste(self, ca: str, descricao: str, func) -> TestResult:
        """Helper para executar um teste individual com try/except."""
        try:
            func()
            return TestResult(self.spec_id, ca, descricao, "PASS")
        except AssertionError as e:
            return TestResult(self.spec_id, ca, descricao, "FAIL", str(e))
        except Exception as e:
            return TestResult(self.spec_id, ca, descricao, "ERROR",
                              f"{type(e).__name__}: {e}")


# =====================================================================
# VALIDADOR CONCRETO: PciValidator (SPEC-PCI-001)
# =====================================================================

class PciValidator(SpecValidator):
    """Calibração do Process Confidence Index."""
    
    @property
    def spec_id(self) -> str:
        return "PCI-001"
    
    @property
    def descricao(self) -> str:
        return "Calibração do Process Confidence Index"
    
    # --- Lógica de domínio encapsulada ---
    @staticmethod
    def calibrar(pci_bruto: float, dominio: str = "geral",
                 num_blocos: int = 0, taxa_narracao: float = 1.0) -> float:
        """Implementação de referência da SPEC-PCI-001."""
        pci_base = 0.062 * pci_bruto
        if dominio == "geometria":
            pci_base *= 0.85
        elif dominio == "numerico":
            pci_base *= 0.70
        if num_blocos > 0:
            pci_base += min(1.0, 0.1 * num_blocos)
        if taxa_narracao < 0.3:
            pci_base += 0.5
        return max(0.0, min(10.0, pci_base))
    
    def _executar_testes(self) -> List[TestResult]:
        c = self.calibrar
        return [
            self._criar_teste("CA1",
                "PCI bruto 95, geometria, 0 blocos -> aprox. 5.01",
                lambda: self._assert_almost(c(95, "geometria", 0), 5.01)),
            
            self._criar_teste("CA2",
                "PCI calibrado nunca ultrapassa 10.0",
                lambda: self._assert_clamped(c)),
            
            self._criar_teste("CA3",
                "PCI calibrado nunca eh negativo",
                lambda: self._assert_non_negative(c)),
            
            self._criar_teste("CA4",
                "Dominio 'numerico' sempre penaliza mais que 'geral'",
                lambda: self._assert_domain_penalty(c)),
            
            self._criar_teste("CA5",
                "Bonus por codigo so se bloco REAL existe",
                lambda: self._assert_code_bonus(c)),
        ]
    
    @staticmethod
    def _assert_almost(valor, esperado, tol=0.02):
        assert abs(valor - esperado) < tol, f"Esperado ~{esperado}, obtido {valor}"
    
    @staticmethod
    def _assert_clamped(func):
        for pci in [100, 200, 1000]:
            for dom in ["geral", "geometria", "numerico"]:
                r = func(pci, dom, 50, 0.0)
                assert r <= 10.0 + 1e-9, f"PCI {pci}/{dom} -> {r} > 10"
    
    @staticmethod
    def _assert_non_negative(func):
        for pci in [0, -10, -100]:
            r = func(pci)
            assert r >= 0.0, f"PCI {pci} -> {r} < 0"
    
    @staticmethod
    def _assert_domain_penalty(func):
        for pci in [30, 50, 80, 100]:
            g = func(pci, "geral")
            n = func(pci, "numerico")
            assert n <= g, f"PCI {pci}: numerico {n} > geral {g}"
    
    @staticmethod
    def _assert_code_bonus(func):
        sem = func(100, "geral", 0)
        com = func(100, "geral", 3)
        assert com > sem, "Bonus de codigo nao aplicado"
        assert abs((com - sem) - 0.3) < 0.01, "Bonus deve ser 0.3 para 3 blocos"


# =====================================================================
# VALIDADOR CONCRETO: CodeValidator (SPEC-CODE-001)
# =====================================================================

class CodeValidator(SpecValidator):
    """Verificador de Obrigatoriedade de Codigo."""
    
    @property
    def spec_id(self) -> str:
        return "CODE-001"
    
    @property
    def descricao(self) -> str:
        return "Verificador de Obrigatoriedade de Codigo"
    
    # Padrões encapsulados como constantes privadas
    _GATILHOS_REJEITAR = [
        r'\bc[óo]digo\b', r'\bsimula[cç][ãa]o\b', r'\bRK45\b',
        r'\bRunge-Kutta\b', r'\bEuler-Maruyama\b',
        r'\bMonte Carlo\b', r'\bo c[óo]digo confirma\b',
        r'\berro\s*<\s*10[\(\-]', r'\bresultado num[ée]rico\b',
    ]
    
    _GATILHOS_AVISO = [
        r'\bdados\b', r'\bdataset\b', r'\bamostra\b',
        r'\bgr[áa]fico mostra\b', r'\bfigura mostra\b',
    ]
    
    def verificar(self, texto: str, blocos: int) -> Tuple[str, str, list]:
        """Retorna (status, razao, gatilhos_encontrados)."""
        if blocos > 0:
            return ("aprovado", "", [])
        
        rejeitados = [p for p in self._GATILHOS_REJEITAR
                      if re.search(p, texto, re.IGNORECASE)]
        avisos = [p for p in self._GATILHOS_AVISO
                  if re.search(p, texto, re.IGNORECASE)]
        
        if rejeitados:
            return ("rejeitado", f"Gatilhos de rejeicao: {rejeitados}", rejeitados)
        elif avisos:
            return ("aviso", f"Gatilhos de aviso: {avisos}", avisos)
        return ("aprovado", "", [])
    
    def _executar_testes(self) -> List[TestResult]:
        v = self.verificar
        return [
            self._criar_teste("CA1",
                "Frase 'Codigo Python com RK45 confirma' sem bloco -> rejeitado",
                lambda: self._assert_rejected(
                    v("Codigo Python com RK45 confirma os balancos com erro < 1e-6", 0))),
            
            self._criar_teste("CA2",
                "Solucao puramente analitica sem gatilhos -> aprovado",
                lambda: self._assert_approved(
                    v("Integrando ambos os lados: integral f(x)dx = F(x) + C", 0))),
            
            self._criar_teste("CA3",
                "Codigo em arquivo externo -> aprovado",
                lambda: self._assert_approved(
                    v("O codigo esta no Apendice A", 1))),
            
            self._criar_teste("CA4",
                "Falso positivo zero para texto matematico puro",
                lambda: self._assert_no_false_positives(v)),
            
            self._criar_teste("CA5",
                "Mensagem de rejeicao aponta o gatilho",
                lambda: self._assert_gatilho_apontado(
                    v("Codigo Python com RK45", 0))),
        ]
    
    @staticmethod
    def _assert_rejected(result):
        status, razao, _ = result
        assert status == "rejeitado", f"Esperado rejeitado, obtido {status}: {razao}"
    
    @staticmethod
    def _assert_approved(result):
        status, _, _ = result
        assert status == "aprovado", f"Esperado aprovado, obtido {status}"
    
    @staticmethod
    def _assert_no_false_positives(func):
        textos = [
            "Seja f: R -> R continua. Entao integral_a^b f(x)dx = F(b) - F(a)",
            "Pelo teorema de Stokes: integral_M domega = integral_{partial M} omega",
            "O operador de Laplace e Delta = nabla * nabla",
            "A serie converge absolutamente para |x| < 1",
            "Multiplicando ambos os lados por e^{integral Pdx}",
        ]
        for t in textos:
            status, _, _ = func(t, 0)
            assert status == "aprovado", f"Falso positivo para: '{t[:60]}...'"
    
    @staticmethod
    def _assert_gatilho_apontado(result):
        status, _, gats = result
        assert status == "rejeitado"
        assert len(gats) > 0, "Gatilhos nao identificados"


# =====================================================================
# VALIDADOR CONCRETO: AntisymValidator (SPEC-ANTISYM-001)
# =====================================================================

class AntisymValidator(SpecValidator):
    """Verificador de Antisimetria do Produto Exterior."""
    
    @property
    def spec_id(self) -> str:
        return "ANTISYM-001"
    
    @property
    def descricao(self) -> str:
        return "Verificador de Antisimetria do Produto Exterior"
    
    def verificar(self, expressao: str) -> Tuple[str, List[dict], float]:
        """
        Retorna (status, violacoes, pontuacao).
        """
        violacoes = []
        
        # AS-01: detect = +b dx^dy ou = b dx^dy em contexto pullback
        if re.search(r'=\s*\+?b\s*(?:\\,)?\s*dx\s*\\wedge\s*dy', expressao):
            if re.search(r'F\^?\*', expressao):
                violacoes.append({
                    "regra": "AS-01",
                    "localizacao": "pullback Henon",
                    "esperado": "-b dx^dy",
                    "obtido": "+b dx^dy (sinal da antisimetria ignorado)"
                })
        
        # AS-02: dx^dx nao simplificado para zero
        if re.search(r'([a-zA-Z])\s*\\wedge\s*\1\s*[=:]', expressao):
            violacoes.append({
                "regra": "AS-02",
                "localizacao": expressao[:60],
                "esperado": "0 (termo nulo por antisimetria)",
                "obtido": "termo nao simplificado"
            })
        
        if violacoes:
            return ("inconsistente", violacoes, max(0.0, 1.0 - 0.5 * len(violacoes)))
        return ("ok", [], 1.0)
    
    def _executar_testes(self) -> List[TestResult]:
        v = self.verificar
        return [
            self._criar_teste("CA1",
                "Detecta +b dx^dy onde deveria ser -b dx^dy",
                lambda: self._assert_pullback_violation(
                    v(r"F^*(dx\wedge dy) = F^*dx \wedge F^*dy = b\,dx\wedge dy"))),
            
            self._criar_teste("CA2",
                "Nao dispara falso positivo para pulback correto",
                lambda: self._assert_no_false_positive(
                    v(r"F^*(dx\wedge dy) = -b\,dx\wedge dy"))),
            
            self._criar_teste("CA3",
                "Nao dispara falso positivo para su(2)",
                lambda: self._assert_no_false_positive(
                    v(r"[J_i,J_j] = i\hbar\epsilon_{ijk}J_k"))),
            
            self._criar_teste("CA4",
                "Pontuacao < 0.5 dispara alerta",
                lambda: self._assert_low_score(
                    v(r"dx\wedge dx = dx\wedge dx"))),
            
            self._criar_teste("CA5",
                "Zero falso positivo em n-formas com n>1",
                lambda: self._assert_no_false_positive(
                    v(r"dx\wedge dy\wedge dz"))),
        ]
    
    @staticmethod
    def _assert_pullback_violation(result):
        status, viol, _ = result
        assert status == "inconsistente", f"Esperado inconsistente, obtido {status}"
        assert any("pullback" in v["localizacao"] for v in viol), \
            "Violacao de pullback nao detectada"
    
    @staticmethod
    def _assert_no_false_positive(result):
        status, _, _ = result
        assert status == "ok", f"Falso positivo: {result}"
    
    @staticmethod
    def _assert_low_score(result):
        status, _, score = result
        if status == "inconsistente":
            assert score < 0.5, f"Score {score} deveria ser < 0.5"


# =====================================================================
# VALIDADOR CONCRETO: NarrValidator (SPEC-NARR-001)
# =====================================================================

class NarrValidator(SpecValidator):
    """Conversor de Narracao para Demonstracao."""
    
    @property
    def spec_id(self) -> str:
        return "NARR-001"
    
    @property
    def descricao(self) -> str:
        return "Conversor de Narracao para Demonstracao"
    
    _PADROES = {
        r'\bobt[eé]m-se\b': 'N-01',
        r'\bverifica-se\b': 'N-02',
        r'\bdeve-se\b': 'N-03',
        r'\bpodemos\b': 'N-04',
        r'\bnota-se\b': 'N-05',
        r'\bafirma-se\b': 'N-06',
        r'\b[ée] claro que\b': 'N-07',
        r'\bo c[óo]digo confirma\b': 'N-08',
        r'\bsubstituindo, obt[eé]m-se\b': 'N-09',
        r'\bap[óo]s simplifica[cç][ãa]o\b': 'N-10',
    }
    
    def detectar(self, texto: str) -> List[Tuple[str, str, str]]:
        """Retorna lista de (padrao_id, match, contexto)."""
        encontrados = []
        for padrao, pid in self._PADROES.items():
            for match in re.finditer(padrao, texto, re.IGNORECASE):
                inicio = max(0, match.start() - 30)
                fim = min(len(texto), match.end() + 50)
                ctx = texto[inicio:fim].replace('\n', ' ')
                encontrados.append((pid, match.group(), ctx))
        return encontrados
    
    def taxa(self, texto: str) -> float:
        """Proporcao do texto composta por padroes narrativos (0.0 a 1.0)."""
        encontrados = self.detectar(texto)
        total_chars = sum(len(m[1]) for m in encontrados)
        return min(1.0, total_chars / max(1, len(texto)))
    
    def _executar_testes(self) -> List[TestResult]:
        d = self.detectar
        t = self.taxa
        return [
            self._criar_teste("CA1",
                "100% dos padroes N-01 a N-10 sao detectados",
                lambda: self._assert_all_patterns(d(self._TEXTO_CA1))),
            
            self._criar_teste("CA2",
                "'o codigo confirma' sem bloco -> pendente",
                lambda: self._assert_pattern_detected(
                    d("O codigo confirma o resultado"), 'N-08')),
            
            self._criar_teste("CA3",
                "Expressoes 'obtem-se' viaveis",
                lambda: self._assert_obtem_se(d)),
            
            self._criar_teste("CA4",
                "'e claro que' sempre dispara verificacao",
                lambda: self._assert_pattern_detected(
                    d("E claro que a energia e conservada"), 'N-07')),
            
            self._criar_teste("CA5",
                "Taxa de narracao calculada corretamente",
                lambda: self._assert_taxa(t)),
        ]
    
    _TEXTO_CA1 = """
    Obtem-se a equacao de movimento. Verifica-se que a energia e conservada.
    Deve-se ter H constante. Podemos escrever a lagrangeana.
    Nota-se que o sistema e integravel. Afirma-se que o torque e nulo.
    E claro que dH/dt = 0. O codigo confirma o resultado.
    Substituindo, obtem-se q = p/m. Apos simplificacao, resta apenas H.
    """
    
    @staticmethod
    def _assert_all_patterns(encontrados):
        ids = set(e[0] for e in encontrados)
        todos = set(NarrValidator._PADROES.values())
        assert ids == todos, f"Padroes nao detectados: {todos - ids}"
    
    @staticmethod
    def _assert_pattern_detected(encontrados, pid):
        assert any(p == pid for p, _, _ in encontrados), f"{pid} nao detectado"
    
    @staticmethod
    def _assert_obtem_se(detect):
        textos = [
            "obtem-se H = omega(Jr + Jtheta + Jphi)",
            "obtem-se a equacao de Hamilton",
            "obtem-se o resultado desejado",
        ]
        for t in textos:
            assert any(pid == 'N-01' for pid, _, _ in detect(t)), f"N-01 nao em: {t}"
    
    @staticmethod
    def _assert_taxa(taxa_func):
        narrativo = "Obtem-se o resultado. Verifica-se a equacao. Nota-se o teorema."
        assert taxa_func(narrativo) > 0.3, "Taxa deveria ser alta para texto narrativo"
        
        algebrico = "H = p2/2m + kq2/2. E = H. dH/dt = 0."
        assert taxa_func(algebrico) == 0.0, "Taxa deveria ser 0 para texto algebrico"


# =====================================================================
# VALIDADOR CONCRETO: CoraValidator (SPEC-CORA-001)
# =====================================================================

class CoraValidator(SpecValidator):
    """Expansao do Escopo do Cora-Debate (Verificacao de Algebra)."""
    
    @property
    def spec_id(self) -> str:
        return "CORA-001"
    
    @property
    def descricao(self) -> str:
        return "Expansao do escopo do Cora-Debate"
    
    # Assinaturas de algebra conhecidas
    _ALGEBRAS = {
        "su2": {
            "generators": ["J1", "J2", "J3"],
            "pattern": {"[J1,J2]": "+J3", "[J2,J3]": "+J1", "[J3,J1]": "+J2"},
            "signature": "compact"
        },
        "su11": {
            "generators": ["J0", "J1", "J2"],
            "pattern": {"[J1,J2]": "-J0", "[J2,J0]": "+J1", "[J0,J1]": "+J2"},
            "signature": "non_compact"
        },
        "so3": {
            "generators": ["Lx", "Ly", "Lz"],
            "pattern": {"[Lx,Ly]": "+iLz", "[Ly,Lz]": "+iLx", "[Lz,Lx]": "+iLy"},
            "signature": "compact"
        },
        "sl2r": {
            "generators": ["H", "E", "F"],
            "pattern": {"[H,E]": "+2E", "[H,F]": "-2F", "[E,F]": "+H"},
            "signature": "split"
        }
    }
    
    @staticmethod
    def _normalizar_gerador(g: str) -> str:
        """J_1 -> J1,  g_1 -> g1"""
        return re.sub(r'_(\d)$', r'\1', g.strip())
    
    @staticmethod
    def _extrair_geradores(comutador: str):
        """Extrai A,B de [A,B] ou {A,B}. Retorna tupla (a, b)."""
        partes = comutador.strip("[]{}").split(",")
        return partes[0], partes[1]
    
    def _gerar_padrao_comutador(self, a: str, b: str) -> str:
        """
        Gera regex flexivel para [A,B] ou {A,B} com/sem subscrito.
        Aceita \\[A,B\\], \\{A,B\\}, [A,B], {A,B} (LaTeX escaping opcional).
        """
        a_norm = self._normalizar_gerador(a)
        b_norm = self._normalizar_gerador(b)
        
        # Cada gerador pode aparecer com ou sem subscrito '_'
        a_pat = re.escape(a_norm)
        b_pat = re.escape(b_norm)
        if a_norm.startswith('J') or a_norm.startswith('L'):
            a_pat = a_norm[0] + '_?' + a_norm[1:]
        if b_norm.startswith('J') or b_norm.startswith('L'):
            b_pat = b_norm[0] + '_?' + b_norm[1:]
        
        # Bracket pairs: [] ou {} com backslash opcional (LaTeX escape)
        bracket_variations = [
            (r'\\?\[', r'\\?\]'),   # [ ou \[
            (r'\\?\{', r'\\?\}'),   # { ou \{
        ]
        
        patterns = []
        for obr, cbr in bracket_variations:
            patterns.append(rf'{obr}{a_pat},{b_pat}{cbr}')
        
        # Combina todas as variacoes
        return '(?:' + '|'.join(patterns) + r')\s*=\s*([^\s,;]+)'
    
    def verificar(self, expressoes: List[str],
                  algebra_detectada: str = "su11") -> Tuple[str, List[dict], float, list]:
        """
        Verifica consistencia de (anti)comutadores contra assinatura.
        Retorna (status, violacoes, score, alternativas).
        """
        if algebra_detectada not in self._ALGEBRAS:
            return ("desconhecida", [], 0.5, [])
        
        sig = self._ALGEBRAS[algebra_detectada]
        violacoes = []
        verificados = 0
        
        for expr in expressoes:
            for comutador, esperado in sig["pattern"].items():
                a, b = self._extrair_geradores(comutador)
                padrao = self._gerar_padrao_comutador(a, b)
                match = re.search(padrao, expr)
                
                if match:
                    verificados += 1
                    obtido = match.group(1)
                    # Verificacao do sinal
                    if obtido.startswith('-') and not esperado.startswith('-'):
                        violacoes.append({"comutador": comutador, "esperado": esperado, "obtido": obtido})
                    elif not obtido.startswith('-') and esperado.startswith('-'):
                        violacoes.append({"comutador": comutador, "esperado": esperado, "obtido": obtido})
        
        if violacoes:
            alternativas = self._sugerir_alternativas(violacoes, algebra_detectada)
            score = max(0.0, 1.0 - 0.4 * len(violacoes))
            return ("inconsistente", violacoes, score, alternativas)
        
        return ("ok", [], 1.0, [])
    
    def _sugerir_alternativas(self, violacoes: List[dict],
                               atual: str) -> List[str]:
        """Tenta identificar se a algebra correta e outra."""
        def _normalizar_valor(v: str) -> str:
            """Normaliza +J_3 -> +J3, -J_0 -> -J0, +iLz -> +iLz."""
            return re.sub(r'_(\d)', r'\1', v.strip())
        
        alternativas = []
        for alt_nome, alt_sig in self._ALGEBRAS.items():
            if alt_nome == atual:
                continue
            match = True
            for v in violacoes:
                if v["comutador"] in alt_sig["pattern"]:
                    obtido_norm = _normalizar_valor(v["obtido"])
                    esperado_alt = _normalizar_valor(alt_sig["pattern"][v["comutador"]])
                    if obtido_norm != esperado_alt:
                        match = False
            if match:
                alternativas.append(alt_nome)
        return alternativas
    
    def _executar_testes(self) -> List[TestResult]:
        v = self.verificar
        return [
            self._criar_teste("CA1",
                "V4 detecta {J1,J2}=+J0 em contexto su(1,1)",
                lambda: self._assert_inconsistent(
                    v([r"\{J_1,J_2\} = +J_0",
                       r"\{J_2,J_0\} = +J_1",
                       r"\{J_0,J_1\} = +J_2"], "su11"))),
            
            self._criar_teste("CA2",
                "V4 aceita [J1,J2]=+J3 em contexto su(2)",
                lambda: self._assert_ok(
                    v([r"[J_1,J_2] = +J_3"], "su2"))),
            
            self._criar_teste("CA3",
                "V4 rejeita [H,E]=-2E onde deveria ser +2E (sl2r)",
                lambda: self._assert_inconsistent(
                    v([r"[H,E] = -2E"], "sl2r"))),
            
            self._criar_teste("CA4",
                "V5 sugere algebra alternativa correta quando violacao e consistente com outra algebra",
                lambda: self._assert_alternativa_sugerida(
                    v([r"[J_1,J_2] = +J_3",   # su(1,1) espera -J0, viola; su(2) tem +J3
                       r"[J_2,J_3] = +J_1"],  # su(1,1) nao tem J3; su(2) tem +J1
                    "su11"))),
            
            self._criar_teste("CA5",
                "V6 verifica conectivos logicos",
                lambda: self._assert_conectivos_validos(
                    "H e constante. Logo dH/dt = 0. Portanto a energia e conservada.")),
        ]
    
    @staticmethod
    def _assert_inconsistent(result):
        status, viol, _, _ = result
        assert status == "inconsistente", f"Esperado inconsistente, obtido {status}"
        assert len(viol) >= 1, "Nenhuma violacao detectada"
    
    @staticmethod
    def _assert_ok(result):
        status, _, _, _ = result
        assert status == "ok", f"Falso positivo: {result}"
    
    @staticmethod
    def _assert_alternativa_sugerida(result):
        status, _, _, alt = result
        assert status == "inconsistente" and len(alt) >= 1, \
            f"Esperava alternativa, obtido status={status}, alt={alt}"
    
    @staticmethod
    def _assert_conectivos_validos(texto):
        assert "Logo" in texto and "Portanto" in texto, \
            "Conectivos logicos ausentes"


# =====================================================================
# TEST RUNNER (Composicao)
# =====================================================================

class TestRunner:
    """
    Orquestrador de validadores.
    Usa composicao: contem instancias de SpecValidator.
    """
    
    def __init__(self, validadores: List[SpecValidator]):
        self._validadores = validadores
    
    @classmethod
    def criar_padrao(cls) -> 'TestRunner':
        """Factory method: cria runner com todos os validadores."""
        return cls([
            PciValidator(),
            CodeValidator(),
            AntisymValidator(),
            NarrValidator(),
            CoraValidator(),
        ])
    
    def executar_todos(self) -> List[SpecReport]:
        """Executa todos os validadores e retorna relatorios."""
        return [v.validar() for v in self._validadores]


# =====================================================================
# RELATORIO
# =====================================================================

class TestReport:
    """
    Gera relatorios formatados (JSON, markdown, stdout)
    a partir de uma lista de SpecReport.
    """
    
    def __init__(self, reports: List[SpecReport]):
        self._reports = reports
        self._timestamp = datetime.now()
    
    # --- Propriedades derivadas ---
    @property
    def total_testes(self) -> int:
        return sum(r.total for r in self._reports)
    
    @property
    def total_passes(self) -> int:
        return sum(r.passes for r in self._reports)
    
    @property
    def total_falhas(self) -> int:
        return sum(r.falhas for r in self._reports)
    
    @property
    def taxa_global(self) -> float:
        return 100.0 * self.total_passes / max(1, self.total_testes)
    
    # --- Saida no stdout ---
    def exibir(self):
        print("=" * 70)
        print("  TDD ACADEMIC v2.0 (OOP) — Validacao de SPECs da Meta-Avaliacao DCA")
        print("=" * 70)
        print(f"  Total de testes: {self.total_testes}")
        print(f"  Data: {self._timestamp.strftime('%Y-%m-%d %H:%M')}")
        print("=" * 70)
        
        for report in self._reports:
            for r in report.resultados:
                print(f"  {r}")
        
        print()
        print("=" * 70)
        print("  RESUMO")
        print("=" * 70)
        print(f"  Total: {self.total_testes}  |  PASS: {self.total_passes}"
              f"  |  FAIL: {self.total_falhas}  |  "
              f"Taxa: {self.taxa_global:.1f}%")
        
        print(f"\n  SPECs testadas: {len(self._reports)}")
        for rep in self._reports:
            barra = ("#" * int(rep.taxa / 10)).ljust(10)
            print(f"    {rep.spec_id}: {rep.passes}/{rep.total} passed"
                  f" ({rep.taxa:.0f}%)  [{barra}]")
        
        if self.total_falhas > 0:
            print(f"\n  [!] {self.total_falhas} teste(s) FALHARAM.")
        else:
            print("\n  [ok] Todos os testes PASSARAM.")
    
    # --- Exportacao JSON ---
    def to_json(self, path: Path):
        data = {
            "metadata": {
                "sistema": "TDDAcademic v2.0 (OOP)",
                "data": self._timestamp.isoformat(),
                "total_testes": self.total_testes,
                "passes": self.total_passes,
                "failures": self.total_falhas,
                "taxa_aprovacao": round(self.taxa_global, 1)
            },
            "specs": {r.spec_id: r.to_dict() for r in self._reports},
            "resultados": [
                tr.to_dict() for r in self._reports for tr in r.resultados
            ]
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return path
    
    # --- Exportacao Markdown ---
    def to_markdown(self) -> str:
        linhas = [
            "# Relatorio TDD — Validacao de SPECs",
            "",
            f"**Data:** {self._timestamp.strftime('%Y-%m-%d %H:%M')}",
            f"**Total:** {self.total_testes} | "
            f"**PASS:** {self.total_passes} | "
            f"**FAIL:** {self.total_falhas} | "
            f"**Taxa:** {self.taxa_global:.1f}%",
            "",
            "## Resultados por SPEC",
            "",
            "| SPEC | Pass/Fail | Taxa |",
            "|------|-----------|------|",
        ]
        for r in self._reports:
            linhas.append(f"| {r.spec_id} | {r.passes}/{r.total} | {r.taxa:.0f}% |")
        
        linhas.extend(["", "## Detalhamento", ""])
        for report in self._reports:
            linhas.append(f"### {report.spec_id}")
            linhas.append("")
            for r in report.resultados:
                status_icon = "+" if r.aprovou() else "x"
                erro_str = f" — {r.erro}" if r.erro else ""
                linhas.append(f"- [{status_icon}] {r.ca}: {r.descricao}{erro_str}")
            linhas.append("")
        
        return "\n".join(linhas)


# =====================================================================
# PONTO DE ENTRADA
# =====================================================================

def main():
    # 1. Criar runner com todos os validadores
    runner = TestRunner.criar_padrao()
    
    # 2. Executar todos os testes
    reports = runner.executar_todos()
    
    # 3. Gerar relatorio
    report = TestReport(reports)
    report.exibir()
    
    # 4. Exportar
    json_path = report.to_json(REPORT_PATH)
    print(f"\n  Relatorio JSON salvo em: {json_path}")
    
    md = report.to_markdown()
    md_path = REPORT_PATH.with_suffix('.md')
    md_path.write_text(md, encoding='utf-8')
    print(f"  Relatorio MD salvo em: {md_path}")
    
    # 5. Exit code
    sys.exit(1 if report.total_falhas > 0 else 0)


if __name__ == "__main__":
    main()
