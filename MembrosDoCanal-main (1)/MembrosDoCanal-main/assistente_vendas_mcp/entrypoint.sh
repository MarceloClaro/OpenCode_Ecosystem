#!/bin/bash

if [ ! -f "database/db.sqlite3" ]; then
    echo "Banco não encontrado. Criando..."
    python init_db.py
else
    echo "Banco já existe. Pulando criação."
fi

uvicorn server:app --host 0.0.0.0 --port 8000 --reload