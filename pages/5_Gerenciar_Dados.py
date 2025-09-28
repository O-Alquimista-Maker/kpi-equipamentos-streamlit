# kpi_equipamentos/pages/5_Gerenciar_Dados.py

import streamlit as st
from database.database_manager import (
    listar_equipamentos_df, excluir_equipamento, atualizar_equipamento,
    listar_manutencoes_df, excluir_manutencao, atualizar_manutencao
)
import datetime
import pandas as pd

# --- Configuração da Página ---
st.set_page_config(page_title="Gerenciar Dados", page_icon="🗃️", layout="wide")
st.title("🗃️ Gerenciar Dados")
st.write("Aqui você pode visualizar, editar e excluir registros das tabelas de equipamentos e manutenções.")

# --- Funções de Diálogo para Edição ---

@st.dialog("✏️ Editar Equipamento")
def dialog_edit_equipamento(item_data):
    st.write(f"Editando Equipamento: **{item_data['descricao']} (S/N: {item_data['numero_serie']})**")
    
    with st.form("form_edit_equipamento"):
        new_numero_serie = st.text_input("Número de Série", value=item_data['numero_serie'])
        new_descricao = st.text_input("Descrição", value=item_data['descricao'])
        new_modelo = st.text_input("Modelo", value=item_data['modelo'])
        new_status = st.selectbox("Status", ["Operacional", "Em Manutenção", "Fora de Operação"], index=["Operacional", "Em Manutenção", "Fora de Operação"].index(item_data['status']))
        new_sistema = st.text_input("Sistema Alocado", value=item_data['sistema_alocado'])
        new_pedido = st.text_input("Pedido de Compra", value=item_data.get('pedido_compra', ''))
        new_data_aq = st.date_input("Data de Aquisição", value=pd.to_datetime(item_data['data_aquisicao']).date())
        new_custo_aq = st.number_input("Custo de Aquisição", value=float(item_data['custo_aquisicao']), format="%.2f")
        new_inicio_g = st.date_input("Início da Garantia", value=pd.to_datetime(item_data['inicio_garantia']).date() if pd.notna(item_data['inicio_garantia']) else None)
        new_fim_g = st.date_input("Fim da Garantia", value=pd.to_datetime(item_data['fim_garantia']).date() if pd.notna(item_data['fim_garantia']) else None)

        if st.form_submit_button("✔️ Salvar Alterações", use_container_width=True):
            try:
                success = atualizar_equipamento(
                    equipamento_id=int(item_data['id']), numero_serie=new_numero_serie, descricao=new_descricao,
                    modelo=new_modelo, status=new_status, sistema_alocado=new_sistema, pedido_compra=new_pedido,
                    data_aquisicao=new_data_aq.isoformat(), custo_aquisicao=float(new_custo_aq),
                    inicio_garantia=new_inicio_g.isoformat() if new_inicio_g else None,
                    fim_garantia=new_fim_g.isoformat() if new_fim_g else None
                )
                if success:
                    st.toast("✅ Equipamento atualizado com sucesso!", icon="🎉")
                    st.session_state.editing_item_id = None
                    st.rerun()
                else:
                    st.toast("❌ Falha ao atualizar o registro.", icon="🔥")
            except Exception as e:
                st.error(f"Ocorreu um erro ao processar a atualização: {e}")

@st.dialog("✏️ Editar Manutenção")
def dialog_edit_manutencao(item_data):
    st.write(f"Editando Manutenção do Equipamento: **{item_data['equipamento_descricao']}**")
    
    equipamentos = listar_equipamentos_df()
    lista_equipamentos = {row['descricao']: row['id'] for index, row in equipamentos.iterrows()}
    
    with st.form("form_edit_manutencao"):
        # Encontrar o índice do equipamento atual para pré-selecionar
        current_equip_id = int(item_data['equipamento_id'])
        equip_desc_list = list(lista_equipamentos.keys())
        equip_id_list = list(lista_equipamentos.values())
        current_index = equip_id_list.index(current_equip_id) if current_equip_id in equip_id_list else 0

        new_equip_desc = st.selectbox("Equipamento", options=equip_desc_list, index=current_index)
        new_data = st.date_input("Data da Manutenção", value=pd.to_datetime(item_data['data_manutencao']).date())
        new_tipo = st.selectbox("Tipo de Manutenção", ["Corretiva", "Preventiva"], index=["Corretiva", "Preventiva"].index(item_data['tipo_manutencao']))
        new_motivo = st.text_area("Motivo/Descrição", value=item_data['motivo_manutencao'])
        new_custo = st.number_input("Custo da Manutenção (R$)", value=float(item_data['custo_manutencao']), format="%.2f")

        if st.form_submit_button("✔️ Salvar Alterações", use_container_width=True):
            try:
                # CORRIGIDO: Chamada da função com argumentos nomeados e corretos
                success = atualizar_manutencao(
                    manutencao_id=int(item_data['id']),
                    equipamento_id=lista_equipamentos[new_equip_desc],
                    data_manutencao=new_data.isoformat(),
                    motivo_manutencao=new_motivo,
                    tipo_manutencao=new_tipo,
                    custo_manutencao=float(new_custo)
                )
                if success:
                    st.toast("✅ Registro de manutenção atualizado com sucesso!", icon="🎉")
                    st.session_state.editing_item_id = None
                    st.rerun()
                else:
                    st.toast("❌ Falha ao atualizar o registro.", icon="🔥")
            except Exception as e:
                st.error(f"Ocorreu um erro ao processar a atualização: {e}")

@st.dialog("🗑️ Confirmar Exclusão")
def confirm_delete_dialog(item_type, item_id, item_desc):
    st.write(f"Você tem certeza que deseja excluir o {item_type}: **{item_desc}**?")
    st.warning("⚠️ Esta ação é irreversível. Todos os dados associados (como manutenções de um equipamento) também serão excluídos.", icon="🚨")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sim, excluir", type="primary", use_container_width=True):
            if item_type == "equipamento":
                excluir_equipamento(item_id)
            elif item_type == "manutenção":
                excluir_manutencao(item_id)
            st.session_state.confirming_delete = None
            st.rerun()
    with col2:
        if st.button("Cancelar", use_container_width=True):
            st.session_state.confirming_delete = None
            st.rerun()

# --- Inicialização do Estado da Sessão ---
if 'editing_item_id' not in st.session_state:
    st.session_state.editing_item_id = None
if 'editing_item_type' not in st.session_state:
    st.session_state.editing_item_type = None
if 'confirming_delete' not in st.session_state:
    st.session_state.confirming_delete = None

# --- Abas para Gerenciamento ---
tab1, tab2 = st.tabs(["Equipamentos", "Manutenções"])

# --- Aba de Equipamentos ---
with tab1:
    st.subheader("Tabela de Equipamentos")
    df_equipamentos = listar_equipamentos_df()

    if df_equipamentos.empty:
        st.info("Nenhum equipamento cadastrado ainda.")
    else:
        # Adiciona colunas de ação
        df_equipamentos['Ações'] = ""
        cols = st.columns([0.4, 0.1, 0.1])
        
        # Exibe os dados com botões
        for index, row in df_equipamentos.iterrows():
            st.markdown("---")
            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                st.write(f"**{row['descricao']}** (S/N: {row['numero_serie']}) - Sistema: {row['sistema_alocado']}")
            with col2:
                if st.button("✏️ Editar", key=f"edit_equip_{row['id']}", use_container_width=True):
                    st.session_state.editing_item_id = row['id']
                    st.session_state.editing_item_type = 'equipamento'
                    st.rerun()
            with col3:
                if st.button("🗑️ Excluir", key=f"del_equip_{row['id']}", use_container_width=True):
                    st.session_state.confirming_delete = {
                        'type': 'equipamento', 'id': row['id'], 'desc': row['descricao']
                    }
                    st.rerun()

# --- Aba de Manutenções ---
with tab2:
    st.subheader("Tabela de Manutenções")
    df_manutencoes = listar_manutencoes_df()

    if df_manutencoes.empty:
        st.info("Nenhum registro de manutenção encontrado.")
    else:
        for index, row in df_manutencoes.iterrows():
            st.markdown("---")
            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                st.write(f"**{row['equipamento_descricao']}** - Data: {pd.to_datetime(row['data_manutencao']).strftime('%d/%m/%Y')} - Custo: R$ {row['custo_manutencao']:.2f}")
            with col2:
                if st.button("✏️ Editar", key=f"edit_manut_{row['id']}", use_container_width=True):
                    st.session_state.editing_item_id = row['id']
                    st.session_state.editing_item_type = 'manutencao'
                    st.rerun()
            with col3:
                if st.button("🗑️ Excluir", key=f"del_manut_{row['id']}", use_container_width=True):
                    st.session_state.confirming_delete = {
                        'type': 'manutenção', 'id': row['id'], 'desc': f"Manutenção de {row['equipamento_descricao']} em {pd.to_datetime(row['data_manutencao']).strftime('%d/%m/%Y')}"
                    }
                    st.rerun()

# --- Lógica para Abrir Diálogos ---
if st.session_state.editing_item_id is not None:
    if st.session_state.editing_item_type == 'equipamento':
        item_data = df_equipamentos[df_equipamentos['id'] == st.session_state.editing_item_id].iloc[0]
        dialog_edit_equipamento(item_data)
    elif st.session_state.editing_item_type == 'manutencao':
        item_data = df_manutencoes[df_manutencoes['id'] == st.session_state.editing_item_id].iloc[0]
        dialog_edit_manutencao(item_data)

if st.session_state.confirming_delete is not None:
    delete_info = st.session_state.confirming_delete
    confirm_delete_dialog(delete_info['type'], delete_info['id'], delete_info['desc'])
