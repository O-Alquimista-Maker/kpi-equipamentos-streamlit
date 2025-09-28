# kpi_equipamentos/database/connection.py

import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import os

# --- Lógica para Carregar Credenciais de Forma Segura ---
try:
    DB_USER = st.secrets["postgres"]["user"]
    DB_PASS = st.secrets["postgres"]["password"]
    DB_HOST = st.secrets["postgres"]["host"]
    DB_PORT = st.secrets["postgres"]["port"]
    DB_NAME = st.secrets["postgres"]["dbname"]
    print("INFO: Credenciais carregadas dos segredos do Streamlit (Modo Produção).")
except (KeyError, FileNotFoundError):
    print("INFO: Segredos do Streamlit não encontrados. Carregando credenciais locais (Modo Desenvolvimento).")
    DB_USER = os.environ.get("DB_USER", "postgres")
    DB_PASS = os.environ.get("DB_PASS", "purplebelt2025") # <<< IMPORTANTE: Coloque a senha do seu banco LOCAL aqui
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = int(os.environ.get("DB_PORT", 5432))
    DB_NAME = os.environ.get("DB_NAME", "kpi_equipamentos_db")

# --- Monta a String de Conexão (DSN) ---
# A adição do '?client_encoding=utf8' força a conexão a usar o encoding correto,
# resolvendo problemas de 'UnicodeDecodeError' em diferentes ambientes.
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?client_encoding=utf8"

# --- Cria o "Motor" de Conexão ---
try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
except Exception as e:
    print(f"ERRO CRÍTICO: Não foi possível criar o motor do SQLAlchemy: {e}")
    st.error(f"Não foi possível conectar ao banco de dados. Verifique as credenciais e a conexão. Erro: {e}")
    engine = None

def get_db_connection():
    """Obtém uma nova conexão do pool de conexões do SQLAlchemy."""
    if engine is None:
        st.error("O motor do banco de dados não foi inicializado.")
        return None
    try:
        conn = engine.connect()
        return conn
    except SQLAlchemyError as e:
        print(f"ERRO: Não foi possível obter conexão do pool do SQLAlchemy: {e}")
        st.error(f"Falha ao conectar ao banco de dados. A aplicação pode não funcionar corretamente. Erro: {e}")
        return None

def get_engine():
    """Retorna a instância do motor do SQLAlchemy."""
    return engine
