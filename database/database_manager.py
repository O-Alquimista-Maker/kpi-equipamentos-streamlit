# kpi_equipamentos/database/database_manager.py

from .connection import get_db_connection, get_engine
import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

# --- Funções de Adição ---

def adicionar_equipamento(numero_serie, descricao, modelo, status, sistema_alocado, data_aquisicao, custo_aquisicao, inicio_garantia, fim_garantia, pedido_compra):
    """Adiciona um novo equipamento ao banco de dados usando SQLAlchemy."""
    conn = get_db_connection()
    if not conn: return False
    
    sql = text("""
        INSERT INTO equipamentos (numero_serie, descricao, modelo, status, sistema_alocado, data_aquisicao, custo_aquisicao, inicio_garantia, fim_garantia, pedido_compra)
        VALUES (:numero_serie, :descricao, :modelo, :status, :sistema_alocado, :data_aquisicao, :custo_aquisicao, :inicio_garantia, :fim_garantia, :pedido_compra)
    """)
    
    try:
        with conn.begin():
            conn.execute(sql, {
                "numero_serie": numero_serie, "descricao": descricao, "modelo": modelo, 
                "status": status, "sistema_alocado": sistema_alocado, "data_aquisicao": data_aquisicao, 
                "custo_aquisicao": custo_aquisicao, "inicio_garantia": inicio_garantia, "fim_garantia": fim_garantia,
                "pedido_compra": pedido_compra
            })
        return True
    except IntegrityError:
        print(f"Erro de integridade: O número de série '{numero_serie}' provavelmente já existe.")
        return False
    except Exception as e:
        print(f"Ocorreu um erro ao adicionar o equipamento: {e}")
        return False
    finally:
        if conn: conn.close()

def adicionar_manutencao(equipamento_id, data_manutencao, tipo_manutencao, motivo_manutencao, custo_manutencao):
    """Adiciona um novo registro de manutenção usando SQLAlchemy."""
    conn = get_db_connection()
    if not conn: return False
    
    sql = text("""
        INSERT INTO manutencoes (equipamento_id, data_manutencao, tipo_manutencao, motivo_manutencao, custo_manutencao)
        VALUES (:equipamento_id, :data_manutencao, :tipo_manutencao, :motivo_manutencao, :custo_manutencao)
    """)
    
    try:
        with conn.begin():
            conn.execute(sql, {
                "equipamento_id": equipamento_id, "data_manutencao": data_manutencao, 
                "tipo_manutencao": tipo_manutencao, "motivo_manutencao": motivo_manutencao, 
                "custo_manutencao": custo_manutencao
            })
        return True
    except Exception as e:
        print(f"Ocorreu um erro ao adicionar a manutenção: {e}")
        return False
    finally:
        if conn: conn.close()

# --- Funções de Leitura (usando Pandas com SQLAlchemy Engine) ---

def listar_equipamentos_df():
    """Busca todos os equipamentos e retorna como um DataFrame do Pandas, usando o engine do SQLAlchemy."""
    engine = get_engine()
    if engine is None: return pd.DataFrame()
    
    query = "SELECT * FROM equipamentos ORDER BY id;"
    try:
        df = pd.read_sql_query(query, engine)
        return df
    except Exception as e:
        print(f"Ocorreu um erro ao listar os equipamentos: {e}")
        return pd.DataFrame()

def listar_manutencoes_df():
    """Busca todas as manutenções com detalhes do equipamento e retorna como DataFrame, usando o engine do SQLAlchemy."""
    engine = get_engine()
    if engine is None: return pd.DataFrame()
    
    query = """
        SELECT m.*, e.descricao as equipamento_descricao, e.numero_serie, e.sistema_alocado
        FROM manutencoes m
        JOIN equipamentos e ON m.equipamento_id = e.id
        ORDER BY m.data_manutencao DESC;
    """
    try:
        df = pd.read_sql_query(query, engine)
        return df
    except Exception as e:
        print(f"Ocorreu um erro ao listar as manutenções: {e}")
        return pd.DataFrame()

# --- Funções de Atualização ---

def atualizar_equipamento(equip_id, numero_serie, descricao, modelo, status, sistema_alocado, data_aquisicao, custo_aquisicao, inicio_garantia, fim_garantia, pedido_compra):
    """Atualiza um equipamento existente usando SQLAlchemy."""
    conn = get_db_connection()
    if not conn: return False
    
    sql = text("""
        UPDATE equipamentos SET
            numero_serie = :numero_serie, descricao = :descricao, modelo = :modelo, status = :status,
            sistema_alocado = :sistema_alocado, data_aquisicao = :data_aquisicao, custo_aquisicao = :custo_aquisicao,
            inicio_garantia = :inicio_garantia, fim_garantia = :fim_garantia, pedido_compra = :pedido_compra
        WHERE id = :equip_id
    """)
    
    try:
        with conn.begin():
            result = conn.execute(sql, {
                "numero_serie": numero_serie, "descricao": descricao, "modelo": modelo, "status": status, 
                "sistema_alocado": sistema_alocado, "data_aquisicao": data_aquisicao, "custo_aquisicao": custo_aquisicao, 
                "inicio_garantia": inicio_garantia, "fim_garantia": fim_garantia, "pedido_compra": pedido_compra,
                "equip_id": equip_id
            })
        return result.rowcount > 0
    except IntegrityError:
        print(f"Erro de integridade: O número de série '{numero_serie}' provavelmente já pertence a outro equipamento.")
        return False
    except Exception as e:
        print(f"Ocorreu um erro ao atualizar o equipamento: {e}")
        return False
    finally:
        if conn: conn.close()

def atualizar_manutencao(manut_id, data_manutencao, tipo_manutencao, motivo_manutencao, custo_manutencao):
    """Atualiza um registro de manutenção usando SQLAlchemy."""
    conn = get_db_connection()
    if not conn: return False
    
    sql = text("""
        UPDATE manutencoes SET
            data_manutencao = :data_manutencao, tipo_manutencao = :tipo_manutencao,
            motivo_manutencao = :motivo_manutencao, custo_manutencao = :custo_manutencao
        WHERE id = :manut_id
    """)
    
    try:
        with conn.begin():
            result = conn.execute(sql, {
                "data_manutencao": data_manutencao, "tipo_manutencao": tipo_manutencao, 
                "motivo_manutencao": motivo_manutencao, "custo_manutencao": custo_manutencao, 
                "manut_id": manut_id
            })
        return result.rowcount > 0
    except Exception as e:
        print(f"Ocorreu um erro ao atualizar a manutenção: {e}")
        return False
    finally:
        if conn: conn.close()

# --- Funções de Exclusão ---

def excluir_equipamento(equip_id):
    """Exclui um equipamento usando SQLAlchemy."""
    conn = get_db_connection()
    if not conn: return False
    
    sql = text("DELETE FROM equipamentos WHERE id = :equip_id")
    
    try:
        with conn.begin():
            result = conn.execute(sql, {"equip_id": equip_id})
        return result.rowcount > 0
    except Exception as e:
        print(f"Ocorreu um erro ao excluir o equipamento: {e}")
        return False
    finally:
        if conn: conn.close()

def excluir_manutencao(manut_id):
    """Exclui um registro de manutenção usando SQLAlchemy."""
    conn = get_db_connection()
    if not conn: return False
    
    sql = text("DELETE FROM manutencoes WHERE id = :manut_id")
    
    try:
        with conn.begin():
            result = conn.execute(sql, {"manut_id": manut_id})
        return result.rowcount > 0
    except Exception as e:
        print(f"Ocorreu um erro ao excluir a manutenção: {e}")
        return False
    finally:
        if conn: conn.close()
