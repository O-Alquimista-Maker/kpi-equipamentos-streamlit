# database/connection.py

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# --- Detalhes da Conexão com o PostgreSQL ---
DB_USER = "postgres"
DB_PASS = "purplebelt2025"  # A senha que você definiu!
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "kpi_equipamentos_db"

# String de Conexão (DSN - Data Source Name) no formato do SQLAlchemy
# Formato: "postgresql+psycopg2://usuario:senha@host:porta/banco"
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Cria um "motor" de conexão que pode ser usado em toda a aplicação
# O pool_pre_ping verifica se a conexão ainda está viva antes de usá-la
try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
except Exception as e:
    print(f"Erro ao criar o motor do SQLAlchemy: {e}")
    engine = None

def get_db_connection():
    """
    Retorna uma nova conexão do pool de conexões do motor SQLAlchemy.
    O Pandas prefere usar o 'engine' diretamente, mas manteremos esta função
    para operações que não usam Pandas, como INSERT, UPDATE, DELETE.
    """
    if engine is None:
        return None
    try:
        # O engine gerencia um "pool" de conexões. Pegamos uma emprestada.
        conn = engine.connect()
        return conn
    except SQLAlchemyError as e:
        print(f"Erro ao obter conexão do pool do SQLAlchemy: {e}")
        return None

# Para o Pandas, é melhor passar o 'engine' diretamente.
# Vamos disponibilizar o engine para ser importado por outros módulos.
def get_engine():
    """Retorna a instância do motor SQLAlchemy."""
    return engine
