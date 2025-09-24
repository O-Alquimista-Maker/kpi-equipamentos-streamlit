# kpi_equipamentos/database/database_manager.py

from database.connection import get_db_connection
import pandas as pd

# --- Funções para 'equipamentos' (CRUD) ---

def adicionar_equipamento(numero_serie, descricao, modelo, sistema_alocado, custo_aquisicao, data_aquisicao, pedido_compra, motivo_compra, inicio_garantia, fim_garantia):
    conn = get_db_connection()
    if not conn: return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO equipamentos (numero_serie, descricao, modelo, sistema_alocado, custo_aquisicao, data_aquisicao, pedido_compra, motivo_compra, inicio_garantia, fim_garantia)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (numero_serie, descricao, modelo, sistema_alocado, custo_aquisicao, data_aquisicao, pedido_compra, motivo_compra, inicio_garantia, fim_garantia))
        conn.commit()
        return True
    except conn.IntegrityError:
        print(f"Erro de Integridade: Número de série '{numero_serie}' já existe.")
        return False
    except Exception as e:
        print(f"Ocorreu um erro ao adicionar o equipamento: {e}")
        return False
    finally:
        if conn:
            conn.close()

def listar_equipamentos_df():
    conn = get_db_connection()
    if not conn: return pd.DataFrame()

    try:
        query = "SELECT * FROM equipamentos"
        df = pd.read_sql_query(query, conn)

        if not df.empty and 'fim_garantia' in df.columns:
            df['fim_garantia'] = pd.to_datetime(df['fim_garantia'], errors='coerce')
            hoje = pd.to_datetime('today').normalize()
            df['em_garantia'] = (df['fim_garantia'] >= hoje).fillna(False).map({True: 'Sim', False: 'Não'})
        else:
            df['em_garantia'] = pd.Series(dtype='str')
        return df
    except Exception as e:
        print(f"Ocorreu um erro ao listar os equipamentos: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()

# kpi_equipamentos/database/database_manager.py
# ... (código existente) ...

# --- Funções para 'equipamentos' (CRUD) ---

# ... (adicionar_equipamento e listar_equipamentos_df existentes) ...

def atualizar_equipamento(equipamento_id: int, numero_serie: str, descricao: str, modelo: str, sistema_alocado: str, custo_aquisicao: float, data_aquisicao: str, status: str) -> bool:
    """
    Atualiza um registro de equipamento existente no banco de dados.
    """
    conn = get_db_connection()
    if not conn: return False

    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE equipamentos
            SET numero_serie = ?,
                descricao = ?,
                modelo = ?,
                sistema_alocado = ?,
                custo_aquisicao = ?,
                data_aquisicao = ?,
                status = ?
            WHERE id = ?
        """, (numero_serie, descricao, modelo, sistema_alocado, custo_aquisicao, data_aquisicao, status, equipamento_id))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Ocorreu um erro ao atualizar o equipamento: {e}")
        return False
    finally:
        if conn:
            conn.close()

def excluir_equipamento(equipamento_id: int) -> bool:
    """
    Exclui um equipamento do banco de dados.
    Primeiro, exclui as manutenções associadas para evitar erros de chave estrangeira.
    """
    conn = get_db_connection()
    if not conn: return False

    try:
        cursor = conn.cursor()
        # Passo 1: Excluir manutenções dependentes (CASCADE)
        cursor.execute("DELETE FROM manutencoes WHERE equipamento_id = ?", (equipamento_id,))
        
        # Passo 2: Excluir o equipamento principal
        cursor.execute("DELETE FROM equipamentos WHERE id = ?", (equipamento_id,))
        
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Ocorreu um erro ao excluir o equipamento e suas manutenções: {e}")
        return False
    finally:
        if conn:
            conn.close()

# --- Funções para 'manutencoes' (CRUD) ---

def adicionar_manutencao(equipamento_id, data_manutencao, motivo_manutencao, tipo_manutencao, custo_manutencao):
    conn = get_db_connection()
    if not conn: return False

    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO manutencoes (equipamento_id, data_manutencao, motivo_manutencao, tipo_manutencao, custo_manutencao)
            VALUES (?, ?, ?, ?, ?)
        """, (equipamento_id, data_manutencao, motivo_manutencao, tipo_manutencao, custo_manutencao))
        conn.commit()
        return True
    except Exception as e:
        print(f"Ocorreu um erro ao adicionar a manutenção: {e}")
        return False
    finally:
        if conn:
            conn.close()

def listar_manutencoes_df():
    conn = get_db_connection()
    if not conn: return pd.DataFrame()

    try:
        query = """
            SELECT
                m.id,
                m.data_manutencao,
                e.descricao AS equipamento_descricao,
                e.numero_serie,
                e.sistema_alocado,
                m.tipo_manutencao,
                m.motivo_manutencao,
                m.custo_manutencao
            FROM
                manutencoes m
            JOIN
                equipamentos e ON m.equipamento_id = e.id
            ORDER BY
                m.data_manutencao DESC;
        """
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        print(f"Ocorreu um erro ao listar as manutenções: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()

def excluir_manutencao(manutencao_id: int) -> bool:
    """
    Exclui um registro de manutenção do banco de dados com base no seu ID.
    """
    conn = get_db_connection()
    if not conn: return False

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM manutencoes WHERE id = ?", (manutencao_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Ocorreu um erro ao excluir a manutenção: {e}")
        return False
    finally:
        if conn:
            conn.close()

def atualizar_manutencao(manutencao_id: int, data_manutencao: str, tipo_manutencao: str, motivo_manutencao: str, custo_manutencao: float) -> bool:
    """
    Atualiza um registro de manutenção existente no banco de dados.
    """
    conn = get_db_connection()
    if not conn: return False

    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE manutencoes
            SET data_manutencao = ?,
                tipo_manutencao = ?,
                motivo_manutencao = ?,
                custo_manutencao = ?
            WHERE id = ?
        """, (data_manutencao, tipo_manutencao, motivo_manutencao, custo_manutencao, manutencao_id))
        conn.commit()
        # Verifica se alguma linha foi realmente afetada/atualizada.
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Ocorreu um erro ao atualizar a manutenção: {e}")
        return False
    finally:
        if conn:
            conn.close()
