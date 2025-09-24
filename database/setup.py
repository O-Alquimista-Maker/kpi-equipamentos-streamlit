# kpi_equipamentos/database/setup.py

from database.connection import get_db_connection

def create_tables():
    """
    Cria as tabelas 'equipamentos' e 'manutencoes' no banco de dados
    se elas ainda não existirem.
    """
    conn = get_db_connection()
    if conn is None:
        print("Não foi possível criar as tabelas: falha na conexão com o banco de dados.")
        return

    try:
        cursor = conn.cursor()

        # Definição da tabela de equipamentos, incluindo custo_aquisicao
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS equipamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_serie TEXT NOT NULL UNIQUE,
                descricao TEXT NOT NULL,
                modelo TEXT,
                sistema_alocado TEXT,
                custo_aquisicao REAL,
                data_aquisicao DATE,
                pedido_compra TEXT,
                motivo_compra TEXT,
                inicio_garantia DATE,
                fim_garantia DATE,
                status TEXT DEFAULT 'Operacional'
            );
        """)

        # Definição da tabela de manutenções
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS manutencoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                equipamento_id INTEGER NOT NULL,
                data_manutencao DATE NOT NULL,
                motivo_manutencao TEXT,
                tipo_manutencao TEXT,
                custo_manutencao REAL,
                FOREIGN KEY (equipamento_id) REFERENCES equipamentos (id)
            );
        """)

        conn.commit()
        print("Tabelas verificadas/criadas com sucesso.")
    except Exception as e:
        print(f"Ocorreu um erro ao criar as tabelas: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    create_tables()
