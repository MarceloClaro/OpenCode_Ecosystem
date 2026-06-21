#!/usr/bin/env python3
"""
TDD — Volume 2 Quality Validator
Valida as especificacoes SDD para o livro V2.
Uso: python .tdd_validate_v2.py
Retorno: 0 se todos os testes passarem, 1 se algum falhar.
"""
import os
import re
import sys

SECTIONS_DIR = r"C:\Users\marce\Documents\OpenCode_Ecosystem\livro-volume2\sections"
ROOT_DIR = r"C:\Users\marce\Documents\OpenCode_Ecosystem\livro-volume2"

class TDDResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def ok(self, test_id, msg):
        self.passed += 1
        print(f"  PASS  {test_id}: {msg}")
    
    def fail(self, test_id, msg):
        self.failed += 1
        self.errors.append(f"FAIL  {test_id}: {msg}")
        print(f"  FAIL  {test_id}: {msg}")
    
    def summary(self):
        print(f"\n{'='*60}")
        print(f"  V2 Quality Validator — Results")
        print(f"{'='*60}")
        print(f"  Passed: {self.passed}")
        print(f"  Failed: {self.failed}")
        print(f"  Status: {'PASS ALL' if self.failed == 0 else f'{self.failed} FAILURE(S)'}")
        print(f"{'='*60}")
        return self.failed == 0


def get_all_chapter_aggregators():
    """Encontra todos os arquivos de capitulo (agregadores OU standalone).
    Considera qualquer arquivo .tex dentro de part[1-4]/ que nao seja
    pre-textual. Nao inclui sub-arquivos com sufixo _01, _02 etc.
    """
    aggregators = []
    for part in ["part1", "part2", "part3", "part4"]:
        part_dir = os.path.join(SECTIONS_DIR, part)
        if not os.path.isdir(part_dir):
            continue
        for f in sorted(os.listdir(part_dir)):
            if not f.endswith(".tex"):
                continue
            # Pular sub-arquivos numerados (ex: _01.tex, _01_introducao.tex)
            if re.search(r'_\d{2}', f):
                continue
            fpath = os.path.join(part_dir, f)
            with open(fpath, "r", encoding="utf-8") as fh:
                content = fh.read()
            # So considerar arquivos com conteudo de seção ou \input
            if "\\section{" in content or "\\input{" in content or "\\subsection{" in content:
                aggregators.append((part, f, fpath))
    return aggregators


def get_all_tex_files():
    """Retorna todos os arquivos .tex do diretorio sections."""
    files = []
    for root, dirs, filenames in os.walk(SECTIONS_DIR):
        for f in filenames:
            if f.endswith(".tex"):
                files.append(os.path.join(root, f))
    return files


def get_inputted_files(aggregator_path):
    """Retorna lista de arquivos incluidos via \\input de um agregador."""
    inputted = []
    with open(aggregator_path, "r", encoding="utf-8") as fh:
        content = fh.read()
    for match in re.finditer(r"\\input\{([^}]+)\}", content):
        rel_path = match.group(1)
        # Tentar com .tex
        fpath = os.path.join(ROOT_DIR, rel_path + ".tex")
        if os.path.exists(fpath):
            inputted.append(os.path.normpath(fpath))
        # Tentar sem extensao
        fpath2 = os.path.join(ROOT_DIR, rel_path)
        if os.path.exists(fpath2) and fpath2 not in inputted:
            inputted.append(os.path.normpath(fpath2))
    return inputted


def main():
    result = TDDResult()
    
    # ============================================================
    # S1 — Badge de Nivel
    # ============================================================
    print("\n--- S1: Badge de Nivel")
    aggregators = get_all_chapter_aggregators()
    chapter_names = {
        "part1": ["Introducao", "Fundamentos", "Medicina"],
        "part2": ["Panorama", "Ortodontia", "Implantodontia", "Endodontia", "Educacao"],
        "part3": ["OpenCode", "Pipeline", "IA", "Plataformas", "Praticas"],
        "part4": ["Impacto", "Etica", "Desafios", "Futuro"],
    }
    
    for part, fname, fpath in aggregators:
        with open(fpath, "r", encoding="utf-8") as fh:
            content = fh.read()
        
        chapter_label = f"{part}/{fname}"
        has_badge = bool(re.search(r"(N[ií]vel[-\s]alvo|N[ií]vel\s*:?\s*N[0-9]|N[ií]vel\s*[0-9])", content, re.IGNORECASE))
        has_sustwin = bool(re.search(r"SUS-Twin|Framework SUS-Twin|SUS-Twin Framework", content, re.IGNORECASE))
        
        if has_badge:
            result.ok(f"S1-{chapter_label}", "Badge de nivel presente")
        else:
            result.fail(f"S1-{chapter_label}", "Badge de nivel AUSENTE")
        
        if has_sustwin:
            result.ok(f"S1b-{chapter_label}", "Referencia ao SUS-Twin presente")
        else:
            result.fail(f"S1b-{chapter_label}", "Referencia ao SUS-Twin AUSENTE")
    
    # ============================================================
    # S2 — Prefacio
    # ============================================================
    print("\n--- S2: Prefacio")
    prefacio_path = os.path.join(SECTIONS_DIR, "00-prefacio.tex")
    if os.path.exists(prefacio_path):
        with open(prefacio_path, "r", encoding="utf-8") as fh:
            prefacio = fh.read()
        if re.search(r"N[íi]vel\s*[0-9]|N[0-9]", prefacio):
            result.ok("S2-levels", "Prefacio menciona niveis N0-N3")
        else:
            result.fail("S2-levels", "Prefacio NAO menciona niveis N0-N3")
        if "SUS-Twin" in prefacio:
            result.ok("S2-sustwin", "Prefacio menciona SUS-Twin")
        else:
            result.fail("S2-sustwin", "Prefacio NAO menciona SUS-Twin")
    
    # ============================================================
    # S3 — Exercicio Pratico nos agregadores
    # ============================================================
    print("\n--- S3: Exercicio Pratico")
    for part, fname, fpath in aggregators:
        # So verificar os que tem subsecoes (coisa diferente de comentarios)
        with open(fpath, "r", encoding="utf-8") as fh:
            content = fh.read()
        
        # Pular agregadores que sao so \input (sem texto proprio)
        text_lines = [l for l in content.split("\n") 
                       if not l.strip().startswith("%") 
                       and "\\input{" not in l
                       and l.strip()]
        if len(text_lines) < 3:
            continue  # Agregador puro, pular
        
        has_exercise = bool(re.search(r"(Projeto|Exerc[ií]cio|Pr[aá]tica|Atividade|Tutorial)", content, re.IGNORECASE))
        chapter_label = f"{part}/{fname}"
        if has_exercise:
            result.ok(f"S3-{chapter_label}", "Projeto/exercicio presente")
        else:
            result.fail(f"S3-{chapter_label}", "Projeto/exercicio AUSENTE")
    
    # ============================================================
    # S4 — Subsecoes listadas no cabecalho do agregador
    # ============================================================
    print("\n--- S4: Subsecoes listadas")
    for part, fname, fpath in aggregators:
        with open(fpath, "r", encoding="utf-8") as fh:
            content = fh.read()
        
        has_sections_list = bool(re.search(r"Se[cç][õo]es:|Subse[cç][õo]es:", content, re.IGNORECASE))
        chapter_label = f"{part}/{fname}"
        if has_sections_list:
            result.ok(f"S4-{chapter_label}", "Subsecoes listadas no cabecalho")
        else:
            result.fail(f"S4-{chapter_label}", "Subsecoes AUSENTES no cabecalho")
    
    # ============================================================
    # S5 — Zero Orfaos
    # ============================================================
    print("\n--- S5: Zero Orfaos")
    all_tex = get_all_tex_files()
    
    # Coletar todos os arquivos inputtados
    inputted_files = set()
    for part, fname, fpath in aggregators:
        for ifile in get_inputted_files(fpath):
            inputted_files.add(ifile)
    
    # Adicionar pre-textuais conhecidos
    known_pretextual = [
        "00-capa.tex", "00-capa-dark.tex", "00-prefacio.tex",
        "01-folha-rosto.tex", "02-ficha-catalografica.tex", 
        "03-dedicatoria.tex", "04-agradecimentos.tex",
        "05-epigrafe.tex", "06-resumo.tex", "07-abstract.tex",
    ]
    # Adicionar os que estao no light.tex/dark.tex
    for main_file in ["light.tex", "dark.tex"]:
        main_path = os.path.join(ROOT_DIR, main_file)
        if os.path.exists(main_path):
            for ifile in get_inputted_files(main_path):
                inputted_files.add(ifile)
    
    orphans = []
    for tf in all_tex:
        norm_tf = os.path.normpath(tf)
        if norm_tf not in inputted_files:
            # Verificar se e pre-textual
            fname = os.path.basename(tf)
            if fname in known_pretextual:
                continue
            # Verificar se esta em appendices/
            if "appendices" in norm_tf:
                continue
            orphans.append(norm_tf)
    
    # Ignorar o proprio spec file
    orphans = [o for o in orphans if ".sdd_v2_specs.md" not in o]
    
    if orphans:
        result.fail(f"S5-orphans", f"{len(orphans)} arquivo(s) orfao(s) encontrado(s):")
        for o in orphans[:10]:
            rel = os.path.relpath(o, ROOT_DIR)
            print(f"       {rel}")
    else:
        result.ok("S5-orphans", "Nenhum arquivo orfao encontrado")
    
    # ============================================================
    # S6 — Metadados da Capa
    # ============================================================
    print("\n--- S6: Metadados da Capa")
    for main_file in ["light.tex", "dark.tex"]:
        main_path = os.path.join(ROOT_DIR, main_file)
        if os.path.exists(main_path):
            with open(main_path, "r", encoding="utf-8") as fh:
                content = fh.read()
            has_v2 = "Volume 2" in content
            has_sustwin = "SUS-Twin" in content or "Framework SUS-Twin" in content
            if has_v2:
                result.ok(f"S6-{main_file}-v2", "Volume 2 no titulo")
            else:
                result.fail(f"S6-{main_file}-v2", "Volume 2 AUSENTE do titulo")
            if has_sustwin:
                result.ok(f"S6-{main_file}-sustwin", "SUS-Twin no titulo")
            else:
                result.fail(f"S6-{main_file}-sustwin", "SUS-Twin AUSENTE do titulo")
    
    # ============================================================
    # W1 — Codigo Python nos exercicios
    # ============================================================
    print("\n--- W1: Codigo Python")
    py_count = 0
    for root, dirs, files in os.walk(SECTIONS_DIR):
        for f in files:
            if f.endswith(".tex"):
                fpath = os.path.join(root, f)
                with open(fpath, "r", encoding="utf-8") as fh:
                    content = fh.read()
                py_count += len(re.findall(r"\\begin\{lstlisting\}\[language=Python", content))
    print(f"  INFO  W1: {py_count} blocos de codigo Python encontrados")
    
    # ============================================================
    # W2 — Tabelas de Metricas
    # ============================================================
    print("\n--- W2: Tabelas de Metricas")
    table_count = 0
    for root, dirs, files in os.walk(SECTIONS_DIR):
        for f in files:
            if f.endswith(".tex"):
                fpath = os.path.join(root, f)
                with open(fpath, "r", encoding="utf-8") as fh:
                    content = fh.read()
                table_count += len(re.findall(r"\\begin\{longtable\}|\\begin\{tabular\}", content))
    print(f"  INFO  W2: {table_count} tabelas encontradas")
    
    # ============================================================
    # W3 — Referencias a ferramentas
    # ============================================================
    print("\n--- W3: Referencia a Ferramentas")
    tool_patterns = [
        (r"DentalSegmentator", "DentalSegmentator"),
        (r"PySUS", "PySUS"),
        (r"MONAI|SwinUNETR|nnU-Net", "MONAI"),
        (r"Open3D", "Open3D"),
        (r"Periomod", "Periomod"),
        (r"FHIR", "FHIR"),
        (r"CaTGO|Tooth-Graph", "CaTGO"),
    ]
    for pattern, name in tool_patterns:
        found = False
        for root, dirs, files in os.walk(SECTIONS_DIR):
            for f in files:
                if f.endswith(".tex"):
                    fpath = os.path.join(root, f)
                    with open(fpath, "r", encoding="utf-8") as fh:
                        content = fh.read()
                    if re.search(pattern, content):
                        found = True
                        break
            if found:
                break
        if found:
            result.ok(f"W3-{name}", f"Ferramenta '{name}' referenciada")
        else:
            result.fail(f"W3-{name}", f"Ferramenta '{name}' NAO referenciada")
    
    # ============================================================
    # S7 — Encoding (todos os .tex sao UTF-8 validos)
    # ============================================================
    print("\n--- S7: Encoding UTF-8")
    cp1252_files = []
    all_tex_files_for_encoding = []
    for root, dirs, files in os.walk(ROOT_DIR):
        for f in files:
            if f.endswith(".tex"):
                all_tex_files_for_encoding.append(os.path.join(root, f))
    for fp in all_tex_files_for_encoding:
        with open(fp, "rb") as fh:
            raw = fh.read()
        try:
            raw.decode("utf-8")
        except UnicodeDecodeError:
            cp1252_files.append(fp)
    if cp1252_files:
        result.fail("S7-encoding", f"{len(cp1252_files)} arquivo(s) cp1252 encontrado(s)")
        for fp in cp1252_files[:5]:
            print(f"       {os.path.relpath(fp, ROOT_DIR)}")
    else:
        result.ok("S7-encoding", f"Todos os {len(all_tex_files_for_encoding)} arquivos .tex sao UTF-8 validos")
    
    # ============================================================
    # S8 — Citacoes (todo \\cite{} tem entrada no .bib)
    # ============================================================
    print("\n--- S8: Integridade de Citacoes")
    bib_path = os.path.join(ROOT_DIR, "referencias.bib")
    if os.path.exists(bib_path):
        with open(bib_path, "r", encoding="utf-8", errors="replace") as fh:
            bib_content = fh.read()
        bib_keys = set(re.findall(r"@\w+\{([^,]+),", bib_content))
        
        all_cite_keys = set()
        for root, dirs, files in os.walk(SECTIONS_DIR):
            for f in files:
                if f.endswith(".tex"):
                    fpath = os.path.join(root, f)
                    with open(fpath, "r", encoding="utf-8", errors="replace") as fh:
                        content = fh.read()
                    for m in re.finditer(r"\\cite\{([^}]+)\}", content):
                        keys = m.group(1).split(",")
                        for k in keys:
                            all_cite_keys.add(k.strip())
        
        missing = all_cite_keys - bib_keys
        if missing:
            result.fail("S8-citations", f"{len(missing)} citacao(oes) sem entrada no .bib")
            for k in sorted(missing)[:10]:
                print(f"       {k}")
        else:
            result.ok("S8-citations", f"Todas as {len(all_cite_keys)} citacoes tem entrada no .bib")
    
    # ============================================================
    # S9 — Labels unicos (sem duplicatas exceto ch:)
    # ============================================================
    print("\n--- S9: Labels Unicos")
    all_labels = {}
    for root, dirs, files in os.walk(SECTIONS_DIR):
        for f in files:
            if f.endswith(".tex"):
                fpath = os.path.join(root, f)
                with open(fpath, "r", encoding="utf-8", errors="replace") as fh:
                    content = fh.read()
                for m in re.finditer(r"\\label\{([^}]+)\}", content):
                    label = m.group(1)
                    if label not in all_labels:
                        all_labels[label] = []
                    all_labels[label].append(os.path.relpath(fpath, ROOT_DIR))
    
    dups = {k: v for k, v in all_labels.items() if len(v) > 1 and not k.startswith("ch:")}
    if dups:
        result.fail("S9-labels", f"{len(dups)} label(ns) duplicado(s) encontrado(s)")
        for label, files in sorted(dups.items()):
            print(f"       {label}: {', '.join(files)}")
    else:
        result.ok("S9-labels", f"Todos os {len(all_labels)} labels sao unicos")
    
    # ============================================================
    # Resumo
    # ============================================================
    success = result.summary()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
