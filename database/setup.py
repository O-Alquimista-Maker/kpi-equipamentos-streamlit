# kpi_equipamentos/database/setup.py

from sqlalchemy import text
from .connection import get_db_connection

def create_tables():
    """Cria as tabelas no banco de dados se elas não existirem."""
    conn = get_db_connection()
    if conn is None:
        print("Não foi possível conectar ao banco de dados para criar as tabelas.")
        return

    try:
        create_equipamentos_table = """
            CREATE TABLE IF NOT EXISTS equipamentos (
                id SERIAL PRIMARY KEY,
                numero_serie VARCHAR(255) UNIQUE NOT NULL,
                descricao TEXT NOT NULL,
                modelo VARCHAR(255),
                status VARCHAR(50),
                sistema_alocado VARCHAR(255),
                pedido_compra VARCHAR(255),
                data_aquisicao DATE,
                custo_aquisicao NUMERIC(10, 2),
                inicio_garantia DATE,
                fim_garantia DATE
            );
        """
        
        # CORRIGIDO: Nome da tabela padronizado para 'manutencoes' (sem 'ç')
        create_manutencoes_table = """
            CREATE TABLE IF NOT EXISTS manutencoes (
                id SERIAL PRIMARY KEY,
                equipamento_id INTEGER REFERENCES equipamentos(id) ON DELETE CASCADE,
                data_manutencao DATE NOT NULL,
                motivo_manutencao TEXT,
                tipo_manutencao VARCHAR(100),
                custo_manutencao NUMERIC(10, 2)
            );
        """
        
        conn.execute(text(create_equipamentos_table))
        conn.execute(text(create_manutencoes_table))
        conn.commit()
        
        print("Tabelas 'equipamentos' e 'manutencoes' verificadas/criadas com sucesso no PostgreSQL.")

    except Exception as e:
        print(f"Ocorreu um erro ao criar as tabelas: {e}")
        conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    create_tables()
