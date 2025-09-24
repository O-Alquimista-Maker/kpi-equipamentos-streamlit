# kpi_equipamentos/pages/6_Detalhes_do_Equipamento.py

import streamlit as st
import pandas as pd
from database.database_manager import listar_equipamentos_df, listar_manutencoes_df
import datetime

# --- Configuração e Carregamento de Dados (sem alterações) ---
st.set_page_config(page_title="Detalhes do Equipamento", page_icon="🔬", layout="wide")
st.title("🔬 Dossiê do Equipamento")
st.markdown("---")

@st.cache_data
def carregar_dados():
    equipamentos = listar_equipamentos_df()
    manutencoes = listar_manutencoes_df()
    if not equipamentos.empty:
        equipamentos['data_aquisicao'] = pd.to_datetime(equipamentos['data_aquisicao'])
        equipamentos['inicio_garantia'] = pd.to_datetime(equipamentos['inicio_garantia'])
        equipamentos['fim_garantia'] = pd.to_datetime(equipamentos['fim_garantia'])
    if not manutencoes.empty:
        manutencoes['data_manutencao'] = pd.to_datetime(manutencoes['data_manutencao'])
    return equipamentos, manutencoes

df_equipamentos, df_manutencoes = carregar_dados()

# --- Widget de Seleção (sem alterações) ---
if df_equipamentos.empty:
    st.warning("Nenhum equipamento cadastrado para exibir detalhes.")
else:
    df_equipamentos['display_name'] = df_equipamentos['descricao'] + " (S/N: " + df_equipamentos['numero_serie'] + ")"
    equipamento_selecionado_display = st.selectbox(
        "Selecione um equipamento para ver seu dossiê:",
        options=df_equipamentos['display_name'],
        index=None,
        placeholder="Escolha um equipamento..."
    )
    st.markdown("---")

    if equipamento_selecionado_display:
        equip_info = df_equipamentos[df_equipamentos['display_name'] == equipamento_selecionado_display].iloc[0]

        # --- Seção de Informações Gerais (sem alterações) ---
        st.header(f"Informações Gerais: {equip_info['descricao']}")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Custo de Aquisição", f"R$ {equip_info['custo_aquisicao']:,.2f}")
            st.markdown(f"**Data de Aquisição:** {equip_info['data_aquisicao'].strftime('%d/%m/%Y') if pd.notna(equip_info['data_aquisicao']) else 'N/A'}")
        with col2:
            st.markdown(f"**Modelo:** {equip_info['modelo']}")
            st.markdown(f"**Sistema Alocado:** {equip_info['sistema_alocado']}")
        with col3:
            st.markdown(f"**Status Atual:** {equip_info['status']}")
            st.markdown(f"**Nº de Série:** {equip_info['numero_serie']}")

        # --- Seção de Garantia (COM A CORREÇÃO) ---
        st.subheader("Status da Garantia")
        
        # --- CORREÇÃO APLICADA AQUI ---
        # Usamos pd.Timestamp('today').normalize() que é a forma correta do Pandas
        # para obter a data de hoje com a hora zerada, garantindo a comparação correta.
        hoje = pd.Timestamp('today').normalize()
        fim_garantia = equip_info['fim_garantia']
        
        if pd.isna(fim_garantia):
            st.warning("Data de fim de garantia não informada.")
        else:
            # A subtração entre dois Timestamps do Pandas já resulta em um objeto 'Timedelta'
            dias_restantes = (fim_garantia - hoje).days
            if dias_restantes >= 0:
                st.success(f"✔️ Em garantia. Expira em {dias_restantes} dias ({fim_garantia.strftime('%d/%m/%Y')}).")
            else:
                st.error(f"❌ Garantia expirada há {-dias_restantes} dias ({fim_garantia.strftime('%d/%m/%Y')}).")

        # --- Seção de Histórico de Manutenções (sem alterações) ---
        st.header("Histórico e Custos de Manutenção")
        manutencoes_do_equip = df_manutencoes[df_manutencoes['numero_serie'] == equip_info['numero_serie']]
        
        if manutencoes_do_equip.empty:
            st.info("Nenhum registro de manutenção para este equipamento.")
        else:
            custo_total_manutencao = manutencoes_do_equip['custo_manutencao'].sum()
            num_manutencoes = len(manutencoes_do_equip)
            
            m_col1, m_col2 = st.columns(2)
            m_col1.metric("Custo Total de Manutenção", f"R$ {custo_total_manutencao:,.2f}")
            m_col2.metric("Número de Manutenções Registradas", num_manutencoes)

            st.dataframe(
                manutencoes_do_equip[['data_manutencao', 'tipo_manutencao', 'motivo_manutencao', 'custo_manutencao']],
                hide_index=True,
                width='stretch', # Corrigido para a nova sintaxe
                column_config={
                    "data_manutencao": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
                    "tipo_manutencao": "Tipo",
                    "motivo_manutencao": "Motivo/Descrição",
                    "custo_manutencao": st.column_config.NumberColumn("Custo (R$)", format="R$ %.2f")
                }
            )
