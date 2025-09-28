# kpi_equipamentos/database/database_manager.py

import pandas as pd
from sqlalchemy import text
from .connection import get_db_connection, get_engine
import datetime
import streamlit as st # IMPORTANTE: Adicionar esta importação

# --- Funções de Equipamentos ---

def adicionar_equipamento(numero_serie, descricao, modelo, status, sistema_alocado, pedido_compra, data_aquisicao, custo_aquisicao, inicio_garantia, fim_garantia):
    """Adiciona um novo equipamento ao banco de dados."""
    conn = get_db_connection()
    if conn is None: return False
    try:
        query = text("""
            INSERT INTO equipamentos (numero_serie, descricao, modelo, status, sistema_alocado, pedido_compra, data_aquisicao, custo_aquisicao, inicio_garantia, fim_garantia)
            VALUES (:numero_serie, :descricao, :modelo, :status, :sistema_alocado, :pedido_compra, :data_aquisicao, :custo_aquisicao, :inicio_garantia, :fim_garantia)
        """)
        params = {
            'numero_serie': numero_serie, 'descricao': descricao, 'modelo': modelo, 'status': status,
            'sistema_alocado': sistema_alocado, 'pedido_compra': pedido_compra, 'data_aquisicao': data_aquisicao,
            'custo_aquisicao': custo_aquisicao, 'inicio_garantia': inicio_garantia, 'fim_garantia': fim_garantia
        }
        conn.execute(query, params)
        conn.commit()
        # Limpa o cache para que a lista de equipamentos seja atualizada na próxima vez que for carregada
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"Ocorreu um erro ao adicionar o equipamento: {e}")
        conn.rollback()
        return False
    finally:
        if conn: conn.close()

@st.cache_data
def listar_equipamentos_df():
    """Lista todos os equipamentos do banco de dados em um DataFrame do Pandas."""
    engine = get_engine()
    if engine is None: return pd.DataFrame()
    try:
        query = "SELECT id, numero_serie, descricao, modelo, status, sistema_alocado, pedido_compra, data_aquisicao, custo_aquisicao, inicio_garantia, fim_garantia FROM equipamentos ORDER BY descricao;"
        
        with engine.connect() as conn:
            df = pd.read_sql_query(text(query), conn)
        
        if not df.empty and 'fim_garantia' in df.columns:
            hoje = pd.to_datetime(datetime.date.today())
            df['fim_garantia'] = pd.to_datetime(df['fim_garantia'], errors='coerce')
            df['em_garantia'] = df['fim_garantia'].apply(lambda x: 'Sim' if pd.notna(x) and x >= hoje else 'Não')
        else:
            df['em_garantia'] = 'Não'
            
        return df
    except Exception as e:
        print(f"Ocorreu um erro ao listar os equipamentos: {e}")
        return pd.DataFrame()

def atualizar_equipamento(equipamento_id, numero_serie, descricao, modelo, status, sistema_alocado, pedido_compra, data_aquisicao, custo_aquisicao, inicio_garantia, fim_garantia):
    """Atualiza as informações de um equipamento existente."""
    conn = get_db_connection()
    if conn is None: return False
    try:
        query = text("""
            UPDATE equipamentos SET
                numero_serie = :numero_serie, descricao = :descricao, modelo = :modelo, status = :status,
                sistema_alocado = :sistema_alocado, pedido_compra = :pedido_compra, data_aquisicao = :data_aquisicao,
                custo_aquisicao = :custo_aquisicao, inicio_garantia = :inicio_garantia, fim_garantia = :fim_garantia
            WHERE id = :id
        """)
        params = {
            'id': equipamento_id, 'numero_serie': numero_serie, 'descricao': descricao, 'modelo': modelo,
            'status': status, 'sistema_alocado': sistema_alocado, 'pedido_compra': pedido_compra,
            'data_aquisicao': data_aquisicao, 'custo_aquisicao': custo_aquisicao,
            'inicio_garantia': inicio_garantia, 'fim_garantia': fim_garantia
        }
        result = conn.execute(query, params)
        conn.commit()
        st.cache_data.clear()
        return result.rowcount > 0
    except Exception as e:
        print(f"Ocorreu um erro ao atualizar o equipamento: {e}")
        conn.rollback()
        return False
    finally:
        if conn: conn.close()

def excluir_equipamento(equipamento_id):
    """Exclui um equipamento e suas manutenções associadas."""
    conn = get_db_connection()
    if conn is None: return False
    try:
        query_manutencoes = text("DELETE FROM manutencoes WHERE equipamento_id = :id")
        conn.execute(query_manutencoes, {'id': equipamento_id})
        
        query_equipamento = text("DELETE FROM equipamentos WHERE id = :id")
        result = conn.execute(query_equipamento, {'id': equipamento_id})
        
        conn.commit()
        st.cache_data.clear()
        return result.rowcount > 0
    except Exception as e:
        print(f"Ocorreu um erro ao excluir o equipamento: {e}")
        conn.rollback()
        return False
    finally:
        if conn: conn.close()

# --- Funções de Manutenções ---

def adicionar_manutencao(equipamento_id, data_manutencao, motivo_manutencao, tipo_manutencao, custo_manutencao):
    """Adiciona um novo registro de manutenção."""
    conn = get_db_connection()
    if conn is None: return False
    try:
        query = text("""
            INSERT INTO manutencoes (equipamento_id, data_manutencao, motivo_manutencao, tipo_manutencao, custo_manutencao)
            VALUES (:equipamento_id, :data_manutencao, :motivo_manutencao, :tipo_manutencao, :custo_manutencao)
        """)
        params = {
            'equipamento_id': equipamento_id, 'data_manutencao': data_manutencao,
            'motivo_manutencao': motivo_manutencao, 'tipo_manutencao': tipo_manutencao,
            'custo_manutencao': custo_manutencao
        }
        conn.execute(query, params)
        conn.commit()
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"Ocorreu um erro ao adicionar a manutenção: {e}")
        conn.rollback()
        return False
    finally:
        if conn: conn.close()

@st.cache_data
def listar_manutencoes_df():
    """Lista todos os registros de manutenção em um DataFrame."""
    engine = get_engine()
    if engine is None: return pd.DataFrame()
    try:
        query = """
            SELECT
                m.id,
                m.equipamento_id,
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
        with engine.connect() as conn:
            df = pd.read_sql_query(text(query), conn)
        return df
    except Exception as e:
        print(f"Ocorreu um erro ao listar as manutenções: {e}")
        return pd.DataFrame()

def atualizar_manutencao(manutencao_id, equipamento_id, data_manutencao, motivo_manutencao, tipo_manutencao, custo_manutencao):
    """Atualiza um registro de manutenção existente."""
    conn = get_db_connection()
    if conn is None: return False
    try:
        query = text("""
            UPDATE manutencoes SET
                equipamento_id = :equipamento_id, data_manutencao = :data_manutencao,
                motivo_manutencao = :motivo_manutencao, tipo_manutencao = :tipo_manutencao,
                custo_manutencao = :custo_manutencao
            WHERE id = :id
        """)
        params = {
            'id': manutencao_id, 'equipamento_id': equipamento_id, 'data_manutencao': data_manutencao,
            'motivo_manutencao': motivo_manutencao, 'tipo_manutencao': tipo_manutencao,
            'custo_manutencao': custo_manutencao
        }
        result = conn.execute(query, params)
        conn.commit()
        st.cache_data.clear()
        return result.rowcount > 0
    except Exception as e:
        print(f"Ocorreu um erro ao atualizar a manutenção: {e}")
        conn.rollback()
        return False
    finally:
        if conn: conn.close()

def excluir_manutencao(manutencao_id):
    """Exclui um registro de manutenção."""
    conn = get_db_connection()
    if conn is None: return False
    try:
        query = text("DELETE FROM manutencoes WHERE id = :id")
        result = conn.execute(query, {'id': manutencao_id})
        conn.commit()
        st.cache_data.clear()
        return result.rowcount > 0
    except Exception as e:
        print(f"Ocorreu um erro ao excluir a manutenção: {e}")
        conn.rollback()
        return False
    finally:
        if conn: conn.close()
