# kpi_equipamentos/database/connection.py

import sqlite3
from sqlite3 import Connection

DATABASE_FILE = "kpi_data.db"

def get_db_connection() -> Connection | None:
    """
    Estabelece e retorna uma conexão com o banco de dados SQLite.
    Adiciona um timeout para evitar erros de 'database is locked'.

    Returns:
        Connection | None: Um objeto de conexão ou None se a conexão falhar.
    """
    try:
        # O timeout=10 diz para a conexão esperar até 10s se o BD estiver ocupado.
        conn = sqlite3.connect(DATABASE_FILE, timeout=10)
        # Configura a conexão para retornar linhas como dicionários (mais fácil de usar).
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None
