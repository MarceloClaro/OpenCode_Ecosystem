#!/usr/bin/env python3
"""
Ponto de entrada canônico: python -m ecosystem [comando] [args...]

Uso:
    python -m ecosystem menu          → Menu adaptativo interativo
    python -m ecosystem status        → Status do ecossistema
    python -m ecosystem doctor        → Diagnóstico completo
    python -m ecosystem run <script>  → Executa script
    python -m ecosystem serve <svc>   → Inicia servidor
    python -m ecosystem sync          → Sincronização
    python -m ecosystem evolve        → Ciclo evolutivo
    python -m ecosystem audit         → Auditoria
    python -m ecosystem test          → Testes
    python -m ecosystem --version     → Versão
    python -m ecosystem --help        → Ajuda
"""

import sys
from ecosystem.cli import main

if __name__ == "__main__":
    sys.exit(main())
