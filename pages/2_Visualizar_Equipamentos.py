# pages/2_Visualizar_Equipamentos.py

import streamlit as st
import pandas as pd
from database.database_manager import listar_equipamentos_df

# --- Configuração da Página ---
st.set_page_config(page_title="Visualizar Equipamentos", page_icon="👉", layout="wide")
st.title("👉 Painel de Equipamentos Cadastrados")
st.markdown("---")

@st.cache_data
def carregar_dados():
    return listar_equipamentos_df()

df_equipamentos = carregar_dados()

if df_equipamentos.empty:
    st.warning("Nenhum equipamento cadastrado. Adicione na página de 'Cadastro'.")
else:
    # ... (código dos filtros) ...
    col1, col2 = st.columns(2)
    with col1:
        sistemas = df_equipamentos['sistema_alocado'].dropna().unique()
        sistema_selecionado = st.multiselect("Filtrar por Sistema:", options=sistemas)
    with col2:
        garantia_status = df_equipamentos['em_garantia'].unique()
        garantia_selecionada = st.multiselect("Filtrar por Garantia:", options=garantia_status)

    df_filtrado = df_equipamentos
    if sistema_selecionado:
        df_filtrado = df_filtrado[df_filtrado['sistema_alocado'].isin(sistema_selecionado)]
    if garantia_selecionada:
        df_filtrado = df_filtrado[df_filtrado['em_garantia'].isin(garantia_selecionada)]


    st.markdown("### Lista de Equipamentos")
    colunas_para_exibir = ['numero_serie', 'descricao', 'modelo', 'sistema_alocado', 'custo_aquisicao', 'data_aquisicao', 'em_garantia', 'fim_garantia', 'status']
    
    st.dataframe(
        df_filtrado[colunas_para_exibir],
        hide_index=True,
        width='stretch', # <<--- CORREÇÃO APLICADA
        column_config={
            "custo_aquisicao": st.column_config.NumberColumn("Custo Aquisição (R$)", format="R$ %.2f"),
            "fim_garantia": st.column_config.DateColumn("Fim da Garantia", format="DD/MM/YYYY"),
            "data_aquisicao": st.column_config.DateColumn("Data de Aquisição", format="DD/MM/YYYY")
        }
    )
    st.info(f"Exibindo {len(df_filtrado)} de {len(df_equipamentos)} equipamentos.")
