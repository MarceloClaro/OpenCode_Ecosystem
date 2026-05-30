"""
core/logger.py - Sistema de Logs Estruturados no SQLite WAL com DI.
Implementa o SQLiteLogHandler para integração com o módulo logging do Python.
"""

import json
import logging
import sqlite3
from pathlib import Path
from typing import Any, Optional


class SQLiteLogHandler(logging.Handler):
    """
    Handler do módulo standard logging que desvia registros de log para uma
    tabela centralizada no banco SQLite WAL do ecossistema.
    """
    def __init__(self, db_path: str | Path) -> None:
        super().__init__()
        self.db_path = Path(db_path)
        self._init_db()

    def _init_db(self) -> None:
        conn = sqlite3.connect(str(self.db_path), timeout=10)
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                level TEXT NOT NULL,
                logger_name TEXT NOT NULL,
                message TEXT NOT NULL,
                payload TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON system_logs (timestamp);
            CREATE INDEX IF NOT EXISTS idx_logs_level ON system_logs (level);
        ''')
        conn.commit()
        conn.close()

    def emit(self, record: logging.LogRecord) -> None:
        # Evita loops recursivos de log nas operações do próprio logger do banco
        if record.name == 'core.logger' or 'system_logs' in record.message:
            return
        
        try:
            payload = None
            if isinstance(record.args, dict):
                payload = json.dumps(record.args, ensure_ascii=False)
            elif record.args:
                payload = json.dumps(list(record.args), ensure_ascii=False, default=str)

            msg = self.format(record)

            conn = sqlite3.connect(str(self.db_path), timeout=5)
            # Define WAL e timeout para concorrência
            conn.execute('PRAGMA journal_mode=WAL')
            conn.execute('PRAGMA busy_timeout=5000')
            conn.execute(
                'INSERT INTO system_logs (level, logger_name, message, payload) VALUES (?, ?, ?, ?)',
                (record.levelname, record.name, msg, payload)
            )
            conn.commit()
            conn.close()
        except Exception:
            self.handleError(record)


class LoggerService:
    """
    Serviço central de leitura, filtragem e gerenciamento de logs estruturados.
    """
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)

    def get_logs(self, limit: int = 100, level: Optional[str] = None, search: Optional[str] = None) -> list[dict]:
        """
        Retorna registros de log formatados e filtrados a partir do banco de dados.
        """
        conn = sqlite3.connect(str(self.db_path), timeout=5)
        conn.row_factory = sqlite3.Row
        
        query = 'SELECT id, timestamp, level, logger_name, message, payload FROM system_logs'
        conditions = []
        params = []
        
        if level:
            conditions.append('level = ?')
            params.append(level.upper())
        if search:
            conditions.append('message LIKE ?')
            params.append(f'%{search}%')
            
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
            
        query += ' ORDER BY id DESC LIMIT ?'
        params.append(limit)
        
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        
        logs = []
        for r in rows:
            payload_data = None
            if r["payload"]:
                try:
                    payload_data = json.loads(r["payload"])
                except Exception:
                    payload_data = r["payload"]
                    
            logs.append({
                "id": r["id"],
                "timestamp": r["timestamp"],
                "level": r["level"],
                "logger": r["logger_name"],
                "message": r["message"],
                "payload": payload_data
            })
            
        conn.close()
        return logs

    def clear_logs(self) -> int:
        """
        Limpa todos os logs do banco. Retorna número de registros deletados.
        """
        conn = sqlite3.connect(str(self.db_path), timeout=5)
        cursor = conn.execute('DELETE FROM system_logs')
        conn.commit()
        conn.close()
        return cursor.rowcount
