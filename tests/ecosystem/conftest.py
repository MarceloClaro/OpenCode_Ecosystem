"""
Configuração de testes para o pacote ecosystem.

Garante que o diretório raiz do projeto esteja no sys.path.
"""

import sys
from pathlib import Path

# Adiciona raiz do projeto ao sys.path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
