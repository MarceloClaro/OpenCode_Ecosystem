import ast
import sys
import argparse
from pathlib import Path

class ReviewerAST(ast.NodeVisitor):
    def __init__(self, filename):
        self.filename = filename
        self.issues = []
        self.current_function = None
        self.depth = 0

    def visit_FunctionDef(self, node):
        self.current_function = node.name
        # Check Law 5: Name length and intention
        if len(node.name) < 3:
            self.issues.append({
                "lei": "Lei 5: Nomeacao Intencional",
                "gravidade": "media",
                "linha": node.lineno,
                "msg": f"Funcao '{node.name}' possui nome curto demais (<= 2 caracteres). Use nomes mais descritivos."
            })
        
        # Check Law 1: Guard Clauses (Early Exit)
        # Check if function has deep nested structure
        self.depth = 0
        self.generic_visit(node)
        self.current_function = None

    def visit_If(self, node):
        self.depth += 1
        if self.depth > 3:
            self.issues.append({
                "lei": "Lei 1: Early Exit / Guard Clauses",
                "gravidade": "alta",
                "linha": node.lineno,
                "msg": f"Aninhamento excessivo detectado no bloco IF (profundidade={self.depth}). Use clausulas de guarda para simplificar."
            })
        self.generic_visit(node)
        self.depth -= 1

    def visit_ExceptHandler(self, node):
        # Check Law 4: Fail Fast, Fail Loud
        # Detect bare except or pass in except
        if node.type is None:
            self.issues.append({
                "lei": "Lei 4: Fail Fast, Fail Loud",
                "gravidade": "critica",
                "linha": node.lineno,
                "msg": "Captura generica de excecoes (except:) sem tipo especificado. Especifique a excecao esperada."
            })
        for body_node in node.body:
            if isinstance(body_node, ast.Pass):
                self.issues.append({
                    "lei": "Lei 4: Fail Fast, Fail Loud",
                    "gravidade": "critica",
                    "linha": body_node.lineno,
                    "msg": "Tratamento de excecao vazio (pass). Falhas silenciosas sao proibidas."
                })
        self.generic_visit(node)

    def visit_Name(self, node):
        # Check Law 5: Poor variable naming
        poor_names = {"x", "y", "z", "temp", "tmp", "val", "data", "chk", "u", "res"}
        if node.id in poor_names and isinstance(node.ctx, ast.Store):
            self.issues.append({
                "lei": "Lei 5: Nomeacao Intencional",
                "gravidade": "baixa",
                "linha": node.lineno,
                "msg": f"Variavel '{node.id}' possui nome generico. Use um nome com significado evidente."
            })

def revisar_arquivo(caminho: Path):
    try:
        conteudo = caminho.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(conteudo, filename=caminho.name)
        reviewer = ReviewerAST(caminho.name)
        reviewer.visit(tree)
        return reviewer.issues
    except SyntaxError as se:
        return [{
            "lei": "Compilacao",
            "gravidade": "critica",
            "linha": se.lineno or 1,
            "msg": f"Erro de sintaxe ao compilar arquivo: {se.msg}"
        }]
    except Exception as e:
        return [{
            "lei": "Sistema",
            "gravidade": "alta",
            "linha": 1,
            "msg": f"Erro ao ler arquivo: {str(e)}"
        }]

def main():
    parser = argparse.ArgumentParser(description="Revisor de codigo automatico alinhado as 5 Leis da Defesa Elegante")
    parser.add_argument("caminho", help="Arquivo ou pasta para revisao")
    args = parser.parse_args()

    caminho = Path(args.caminho)
    issues_encontradas = {}
    
    if caminho.is_file():
        if caminho.suffix == ".py":
            issues = revisar_arquivo(caminho)
            if issues:
                issues_encontradas[str(caminho)] = issues
    elif caminho.is_dir():
        for f in caminho.rglob("*.py"):
            issues = revisar_arquivo(f)
            if issues:
                issues_encontradas[str(f)] = issues

    if not issues_encontradas:
        print("Parabens! Nenhum desvio das 5 Leis da Defesa Elegante foi encontrado.")
        sys.exit(0)

    print("\n=== RELATORIO DE REVISAO AUTOMATICA ===\n")
    total_issues = 0
    for arq, issues in issues_encontradas.items():
        print(f"Arquivo: {arq}")
        for issue in issues:
            total_issues += 1
            print(f"  [{issue['gravidade'].upper()}] Linha {issue['linha']} | {issue['lei']} - {issue['msg']}")
        print()

    print(f"Total de inconformidades encontradas: {total_issues}")
    sys.exit(1 if total_issues > 0 else 0)

if __name__ == "__main__":
    main()
