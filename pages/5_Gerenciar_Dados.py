# kpi_equipamentos/pages/5_Gerenciar_Dados.py

import streamlit as st
import pandas as pd
from database.database_manager import (
    listar_manutencoes_df, excluir_manutencao, atualizar_manutencao,
    listar_equipamentos_df, excluir_equipamento, atualizar_equipamento
)
import datetime

# --- Configuração da Página ---
st.set_page_config(page_title="Gerenciar Dados", page_icon="🗂️", layout="wide")
st.title("🗂️ Gerenciamento de Dados do Sistema")
st.markdown("---")

# --- Inicialização do Session State ---
# Para edição
if 'editing_item_id' not in st.session_state:
    st.session_state.editing_item_id = None
if 'editing_entity_type' not in st.session_state:
    st.session_state.editing_entity_type = None
# NOVO: Para exclusão
if 'deleting_item_id' not in st.session_state:
    st.session_state.deleting_item_id = None
if 'deleting_entity_type' not in st.session_state:
    st.session_state.deleting_entity_type = None

# --- Diálogos ---

# Diálogo de Edição de Manutenção (sem alterações)
@st.dialog("Editar Registro de Manutenção")
def dialog_edit_manutencao(item_data):
    # ... (código do diálogo de edição de manutenção, sem alterações)
    data_atual = item_data['data_manutencao']
    with st.form("edit_form_manutencao"):
        new_data = st.date_input("Data da Manutenção", value=data_atual, format="DD/MM/YYYY")
        new_tipo = st.selectbox("Tipo", options=["Corretiva", "Preventiva"], index=["Corretiva", "Preventiva"].index(item_data['tipo_manutencao']))
        new_custo = st.number_input("Custo (R$)", value=float(item_data['custo_manutencao']), format="%.2f")
        new_motivo = st.text_area("Motivo", value=item_data['motivo_manutencao'])
        if st.form_submit_button("Salvar", type="primary"):
            success = atualizar_manutencao(int(item_data['id']), new_data.isoformat(), new_tipo, new_motivo, float(new_custo))
            if success: st.toast("Registro atualizado!", icon="✅"); st.session_state.editing_item_id = None; st.cache_data.clear(); st.rerun()
            else: st.error("Falha ao atualizar.")

# Diálogo de Edição de Equipamento (sem alterações)
@st.dialog("Editar Registro de Equipamento")
def dialog_edit_equipamento(item_data):
    # ... (código do diálogo de edição de equipamento, sem alterações)
    data_aq_atual = pd.to_datetime(item_data['data_aquisicao']).date() if pd.notna(item_data['data_aquisicao']) else None
    with st.form("edit_form_equipamento"):
        st.text_input("Descrição", value=item_data['descricao'], disabled=True)
        new_numero_serie = st.text_input("Número de Série", value=item_data['numero_serie'])
        new_modelo = st.text_input("Modelo", value=item_data['modelo'])
        new_sistema = st.text_input("Sistema Alocado", value=item_data['sistema_alocado'])
        new_custo = st.number_input("Custo de Aquisição (R$)", value=float(item_data['custo_aquisicao']), format="%.2f")
        new_data_aq = st.date_input("Data de Aquisição", value=data_aq_atual, format="DD/MM/YYYY")
        new_status = st.selectbox("Status", options=["Operacional", "Em Manutenção", "Desativado"], index=["Operacional", "Em Manutenção", "Desativado"].index(item_data['status']))
        if st.form_submit_button("Salvar", type="primary"):
            success = atualizar_equipamento(int(item_data['id']), new_numero_serie, item_data['descricao'], new_modelo, new_sistema, float(new_custo), new_data_aq.isoformat() if new_data_aq else None, new_status)
            if success: st.toast("Equipamento atualizado!", icon="✅"); st.session_state.editing_item_id = None; st.cache_data.clear(); st.rerun()
            else: st.error("Falha ao atualizar.")

# --- NOVO DIÁLOGO DE CONFIRMAÇÃO DE EXCLUSÃO ---
@st.dialog("Confirmar Exclusão")
def dialog_confirm_delete(entity_type: str, item_id: int):
    st.warning(f"**Atenção:** Você tem certeza que deseja excluir o {entity_type} de ID `{item_id}`?")
    if entity_type == 'equipamento':
        st.error("Excluir um equipamento também removerá **todo o seu histórico de manutenções** permanentemente.")
    
    col1, col2 = st.columns(2)
    if col1.button("Cancelar", use_container_width=True):
        st.session_state.deleting_item_id = None
        st.rerun()
    
    if col2.button("Confirmar Exclusão", type="primary", use_container_width=True):
        success = False
        if entity_type == 'manutenção':
            success = excluir_manutencao(item_id)
        elif entity_type == 'equipamento':
            success = excluir_equipamento(item_id)
        
        if success:
            st.toast(f"{entity_type.capitalize()} excluído com sucesso!", icon="✅")
            st.session_state.deleting_item_id = None
            st.cache_data.clear()
            st.rerun()
        else:
            st.error("Falha ao excluir o registro.")

# --- Lógica Principal ---
# Abre o diálogo de exclusão se um item estiver marcado
if st.session_state.deleting_item_id:
    dialog_confirm_delete(st.session_state.deleting_entity_type, st.session_state.deleting_item_id)

# --- Abas ---
tab_manutencoes, tab_equipamentos = st.tabs(["Gerenciar Manutenções", "Gerenciar Equipamentos"])

# --- Aba de Manutenções ---
with tab_manutencoes:
    st.header("Registros de Manutenção")
    df_manutencoes = listar_manutencoes_df()
    if not df_manutencoes.empty: df_manutencoes['data_manutencao'] = pd.to_datetime(df_manutencoes['data_manutencao'])

    if st.session_state.editing_item_id and st.session_state.editing_entity_type == 'manutencao':
        if st.session_state.editing_item_id in df_manutencoes['id'].values:
            dialog_edit_manutencao(df_manutencoes[df_manutencoes['id'] == st.session_state.editing_item_id].iloc[0])

    if df_manutencoes.empty: st.warning("Nenhum registro de manutenção encontrado.")
    else:
        for _, row in df_manutencoes.iterrows():
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 2, 1])
                c1.subheader(f"{row['equipamento_descricao']} (S/N: {row['numero_serie']})")
                c1.markdown(f"**Data:** {row['data_manutencao'].strftime('%d/%m/%Y')} | **Tipo:** {row['tipo_manutencao']}")
                c2.markdown(f"**Custo:** R$ {row['custo_manutencao']:.2f}")
                c2.caption(f"Motivo: {row['motivo_manutencao']}")
                
                # --- FLUXO DE EXCLUSÃO MODIFICADO ---
                if c3.button("🗑️", key=f"del_m_{row['id']}", help="Excluir Manutenção"):
                    st.session_state.deleting_item_id = row['id']
                    st.session_state.deleting_entity_type = 'manutenção'
                    st.rerun()
                
                if c3.button("✏️", key=f"edit_m_{row['id']}", help="Editar Manutenção"):
                    st.session_state.editing_item_id = row['id']; st.session_state.editing_entity_type = 'manutencao'; st.rerun()

# --- Aba de Equipamentos ---
with tab_equipamentos:
    st.header("Registros de Equipamentos")
    df_equipamentos = listar_equipamentos_df()

    if st.session_state.editing_item_id and st.session_state.editing_entity_type == 'equipamento':
        if st.session_state.editing_item_id in df_equipamentos['id'].values:
            dialog_edit_equipamento(df_equipamentos[df_equipamentos['id'] == st.session_state.editing_item_id].iloc[0])

    if df_equipamentos.empty: st.warning("Nenhum equipamento encontrado.")
    else:
        for _, row in df_equipamentos.iterrows():
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 2, 1])
                c1.subheader(f"{row['descricao']} (S/N: {row['numero_serie']})")
                c1.markdown(f"**Modelo:** {row['modelo']} | **Sistema:** {row['sistema_alocado']}")
                c2.markdown(f"**Custo Aquisição:** R$ {row['custo_aquisicao']:.2f}")
                c2.markdown(f"**Status:** {row['status']}")
                
                # --- FLUXO DE EXCLUSÃO MODIFICADO ---
                if c3.button("🗑️", key=f"del_e_{row['id']}", help="Excluir Equipamento e Manutenções Associadas"):
                    st.session_state.deleting_item_id = row['id']
                    st.session_state.deleting_entity_type = 'equipamento'
                    st.rerun()
                
                if c3.button("✏️", key=f"edit_e_{row['id']}", help="Editar Equipamento"):
                    st.session_state.editing_item_id = row['id']; st.session_state.editing_entity_type = 'equipamento'; st.rerun()

