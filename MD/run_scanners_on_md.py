import sys
import os
import subprocess
from pathlib import Path

# Add the academic-audit directory to system path to import NoologicalScanner
sys.path.insert(0, r"C:\Users\marce\Documents\OpenCode_Ecosystem\skills\system\academic-audit")

try:
    from noological_scanner import NoologicalScanner
except ImportError as e:
    print(f"Could not import NoologicalScanner: {e}")
    NoologicalScanner = None

class MockParagraph:
    def __init__(self, text):
        self.text = text

class MockAuditTrail:
    def __init__(self, paragraphs):
        self.paragraphs = {str(i): MockParagraph(text) for i, text in enumerate(paragraphs)}
        self.citation_map = []

def run_noological_for_md(md_path, out_report_path):
    if not NoologicalScanner:
        print("NoologicalScanner is not available, skipping.")
        return
        
    print(f"\nRunning Noological Scanner on {md_path.name}...")
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    paragraphs = []
    # Split by double newlines, clean comments and whitespace
    for p in content.split("\n\n"):
        p_clean = p.strip()
        if p_clean and not p_clean.startswith("%"):
            paragraphs.append(p_clean)
            
    print(f"Loaded {len(paragraphs)} paragraphs from {md_path.name}")
    audit_trail = MockAuditTrail(paragraphs)
    
    scanner = NoologicalScanner()
    scan_results = scanner.scan(audit_trail, research_domain="educacao")
    scanner.save_report(out_report_path)
    
    print(f"Saved noological report to {out_report_path}")
    print(f"Coverage: {scan_results['overall_coverage_pct']}% | Grade: {scan_results['completeness_grade']}")

def run_cmd_scanner(scanner_script, input_md, out_report_txt):
    print(f"\nRunning {Path(scanner_script).name} on {Path(input_md).name}...")
    cmd = [
        "python",
        scanner_script,
        "--input",
        str(input_md)
    ]
    try:
        # Run without text=True to get raw bytes and decode manually with replace
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        stdout_str = res.stdout.decode('utf-8', errors='replace')
        with open(out_report_txt, "w", encoding="utf-8") as f:
            f.write(stdout_str)
        print(f"Saved scanner output to {out_report_txt}")
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        stdout_err = e.stdout.decode('utf-8', errors='replace') if e.stdout else ""
        stderr_err = e.stderr.decode('utf-8', errors='replace') if e.stderr else ""
        print(f"Stdout: {stdout_err}")
        print(f"Stderr: {stderr_err}")

def main():
    md_dir = Path(r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\MD")
    latex_dir = Path(r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\dissertacao-latex")
    
    md_files = [
        md_dir / "01_Trabalho_Final.md",
        md_dir / "02-Dissertação_EstagioAtual.md"
    ]
    
    anti_ai = str(latex_dir / "anti_ai_scanner.py")
    anti_plag = str(latex_dir / "anti_plagiarism_scanner.py")
    
    for md_file in md_files:
        if not md_file.exists():
            print(f"MD file not found: {md_file}")
            continue
            
        base_name = md_file.stem
        
        # 1. Noological Scan
        noo_report = md_dir / f"RELATORIO_NOOLOGICO_{base_name}.md"
        run_noological_for_md(md_file, noo_report)
        
        # 2. Anti-AI Scan
        ai_report = md_dir / f"REPORT_ANTIAI_{base_name}.txt"
        run_cmd_scanner(anti_ai, md_file, ai_report)
        
        # 3. Anti-Plagiarism Scan
        plag_report = md_dir / f"REPORT_ANTIPLAGIARISM_{base_name}.txt"
        run_cmd_scanner(anti_plag, md_file, plag_report)

if __name__ == "__main__":
    main()
