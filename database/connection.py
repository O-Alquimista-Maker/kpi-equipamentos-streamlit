# kpi_equipamentos/database/connection.py

import os
import streamlit as st
from sqlalchemy import create_engine, exc

# Tenta carregar dos segredos do Streamlit (quando em produção na nuvem)
try:
    # Esta verificação agora é segura por causa da lógica abaixo
    if hasattr(st, 'secrets') and "postgres" in st.secrets:
        DB_USER = st.secrets["postgres"]["user"]
        DB_PASS = st.secrets["postgres"]["password"]
        DB_HOST = st.secrets["postgres"]["host"]
        DB_PORT = st.secrets["postgres"]["port"]
        DB_NAME = st.secrets["postgres"]["dbname"]
        print("INFO: Credenciais carregadas dos segredos do Streamlit (Modo Produção).")
    else:
        # Força a queda para o except se st.secrets não tiver a chave
        raise KeyError("Chave 'postgres' não encontrada nos segredos.")

# Se der erro (porque st.secrets não existe ou não tem a chave), usa as credenciais locais.
except (KeyError, FileNotFoundError, st.errors.StreamlitAPIException):
    print("INFO: Segredos do Streamlit não encontrados ou incompletos. Carregando credenciais locais (Modo Desenvolvimento).")
    
    DB_USER = os.environ.get("DB_USER", "postgres")
    DB_PASS = os.environ.get("DB_PASS", "purplebelt2025") # <<< IMPORTANTE: Coloque a senha do seu banco LOCAL aqui
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = int(os.environ.get("DB_PORT", 5432))
    DB_NAME = os.environ.get("DB_NAME", "kpi_equipamentos_db")

# --- Cria a String de Conexão e o Engine ---

# String de conexão base
db_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ADICIONA O PARÂMETRO SSL QUANDO EM PRODUÇÃO
if hasattr(st, 'secrets') and "postgres" in st.secrets:
    db_url += "?sslmode=require"
    print("INFO: SSL mode 'require' adicionado à URL de conexão (Modo Produção).")

# Cria o engine do SQLAlchemy
try:
    engine = create_engine(db_url)
    print("INFO: Engine do SQLAlchemy criado com sucesso.")
except Exception as e:
    print(f"ERRO: Falha ao criar o engine do SQLAlchemy. Erro: {e}")
    engine = None

def get_engine():
    """Retorna a instância do engine do SQLAlchemy."""
    return engine

def get_db_connection():
    """Estabelece e retorna uma nova conexão com o banco de dados."""
    if engine is None:
        st.error("Falha ao conectar ao banco de dados. A aplicação pode não funcionar corretamente.")
        return None
    try:
        connection = engine.connect()
        return connection
    except exc.OperationalError as e:
        st.error(f"Falha ao conectar ao banco de dados. A aplicação pode não funcionar corretamente. Erro: {e}")
        return None


