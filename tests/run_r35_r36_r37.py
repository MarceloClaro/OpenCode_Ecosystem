#!/usr/bin/env python3
"""
Runner integrado dos testes R35-R37:
  Capability Registration Framework (SPEC-080)
  Research Skills Implementation (SPEC-081)
  Injector + Coverage Expansion (R37)

Uso:
    python tests/run_r35_r36_r37.py              # todos os testes
    python tests/run_r35_r36_r37.py -v            # verbose
    python tests/run_r35_r36_r37.py --spec 80     # apenas SPEC-080
    python tests/run_r35_r36_r37.py --skills      # apenas skills
    python tests/run_r35_r36_r37.py --html        # relatório HTML
"""
import subprocess
import sys
import os

BASE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(BASE)

TEST_GROUPS = {
    80: os.path.join(BASE, "test_r35_capability_registration.py"),
    81: os.path.join(BASE, "test_r35_research_skills.py"),
}

def main():
    args = sys.argv[1:]
    cmd = [sys.executable, "-m", "pytest"]

    # Parse flags
    spec_filters = []
    only_skills = False
    skip_next = False
    for i, a in enumerate(args):
        if skip_next:
            skip_next = False
            continue
        if a == "--skills":
            only_skills = True
        elif a.startswith("--spec="):
            spec_filters.append(int(a.split("=")[1]))
        elif a.startswith("--spec"):
            if i + 1 < len(args) and not args[i + 1].startswith("-"):
                spec_filters.append(int(args[i + 1]))
                skip_next = True

    # Resolve test files
    if spec_filters:
        for s in spec_filters:
            if s not in TEST_GROUPS:
                print(f"SPEC-{s:03d} não encontrada. Opções: {list(TEST_GROUPS.keys())}")
                sys.exit(1)
            cmd.append(TEST_GROUPS[s])
    elif only_skills:
        cmd.append(TEST_GROUPS[81])
    else:
        cmd.extend(TEST_GROUPS.values())

    # Flags
    if "--cov" in args or "--coverage" in args:
        cmd.extend(["--cov", "--cov-report=term-missing"])
    if "--html" in args:
        cmd.extend(["--html=report-r35.html", "--self-contained-html"])
    if "--verbose" in args or "-v" in args:
        if "-v" not in cmd:
            cmd.append("-v")

    print(f"R35-R37 Test Runner")
    print(f"{'='*60}")
    print(f"$ {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd, cwd=PROJECT, text=True)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
