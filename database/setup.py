# database/setup.py

from .connection import get_db_connection
from sqlalchemy import text

def criar_tabelas():
    """Cria as tabelas 'equipamentos' e 'manutencoes' no banco de dados usando SQLAlchemy."""
    conn = get_db_connection()
    if conn is None:
        print("Não foi possível conectar ao banco de dados para criar as tabelas.")
        return

    try:
        with conn.begin() as transaction:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS equipamentos (
                    id SERIAL PRIMARY KEY,
                    numero_serie VARCHAR(100) UNIQUE NOT NULL,
                    descricao VARCHAR(255) NOT NULL,
                    modelo VARCHAR(100),
                    status VARCHAR(50),
                    sistema_alocado VARCHAR(100),
                    data_aquisicao DATE,
                    custo_aquisicao NUMERIC(10, 2),
                    inicio_garantia DATE,
                    fim_garantia DATE,
                    pedido_compra VARCHAR(100)  -- GARANTIR QUE ESTA LINHA ESTÁ AQUI
                );
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS manutencoes (
                    id SERIAL PRIMARY KEY,
                    equipamento_id INTEGER NOT NULL,
                    data_manutencao DATE NOT NULL,
                    tipo_manutencao VARCHAR(50) NOT NULL,
                    motivo_manutencao TEXT,
                    custo_manutencao NUMERIC(10, 2),
                    FOREIGN KEY (equipamento_id) REFERENCES equipamentos (id) ON DELETE CASCADE
                );
            """))
        print("Tabelas 'equipamentos' e 'manutencoes' verificadas/criadas com sucesso no PostgreSQL.")
    except Exception as e:
        print(f"Ocorreu um erro ao criar as tabelas: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    criar_tabelas()
