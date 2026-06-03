#!/usr/bin/env python3
"""
Wrapper para executar Phase B com encoding UTF-8 forçado.

Soluciona problema de charmap em Windows (stdout/stderr em cp1252).
"""

import sys
import io

# Forçar UTF-8 em stdout/stderr no Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer,
        encoding='utf-8',
        errors='replace'
    )
    sys.stderr = io.TextIOWrapper(
        sys.stderr.buffer,
        encoding='utf-8',
        errors='replace'
    )

from pipeline_phase_b import PipelinePhaseB

def main():
    """Executar Phase B com UTF-8."""
    pipeline = PipelinePhaseB()
    results = pipeline.run(top_n=3, max_iterations=2)
    pipeline.save_results(results)
    
    print("\n✅ Phase B completado!")
    print(f"  Sucessos: {results['success_count']}")
    print(f"  Parciais: {results['partial_count']}")
    print(f"  Falhas: {results['failed_count']}")

if __name__ == "__main__":
    main()
