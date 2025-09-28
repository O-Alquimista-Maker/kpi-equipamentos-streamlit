# kpi_equipamentos/pages/2_Visualizar_Equipamentos.py

import streamlit as st
import pandas as pd
from database.database_manager import listar_equipamentos_df
from PIL import Image
import datetime

# --- Configuração da Página ---
try:
    favicon = Image.open("assets/seu_logo.png")
    st.set_page_config(page_title="Visualizar Equipamentos", page_icon=favicon, layout="wide")
except FileNotFoundError:
    st.set_page_config(page_title="Visualizar Equipamentos", page_icon="🔬", layout="wide")

st.title("📋 Lista de Equipamentos Cadastrados")
st.markdown("---")

# --- Carregamento dos Dados ---
df_equipamentos = listar_equipamentos_df()

# --- VERIFICAÇÃO E CORREÇÃO ---
# Se o DataFrame não estiver vazio, vamos processar as colunas
if not df_equipamentos.empty:
    
    # Converte as colunas de data para o formato datetime do pandas
    df_equipamentos['inicio_garantia'] = pd.to_datetime(df_equipamentos['inicio_garantia'], errors='coerce')
    df_equipamentos['fim_garantia'] = pd.to_datetime(df_equipamentos['fim_garantia'], errors='coerce')

    # --- LÓGICA PARA CRIAR A COLUNA VIRTUAL 'em_garantia' ---
    hoje = datetime.datetime.now().date()
    
    # Define uma função para aplicar a lógica
    def verificar_garantia(row):
        if pd.notna(row['fim_garantia']):
            return "Sim" if row['fim_garantia'].date() >= hoje else "Não"
        return "Não Informado"

    # Aplica a função para criar a nova coluna
    df_equipamentos['em_garantia'] = df_equipamentos.apply(verificar_garantia, axis=1)
    
    # --- FIM DA LÓGICA DE CRIAÇÃO DA COLUNA ---

    st.info(f"Total de equipamentos cadastrados: **{len(df_equipamentos)}**")

    # --- Filtros ---
    st.sidebar.header("Filtros de Visualização")
    
    # Filtro por Sistema
    sistemas = sorted(df_equipamentos['sistema_alocado'].dropna().unique())
    sistemas_selecionados = st.sidebar.multiselect("Filtrar por Sistema:", options=sistemas, default=sistemas)

    # Filtro por Status de Garantia
    # AGORA ESTA LINHA VAI FUNCIONAR, POIS A COLUNA 'em_garantia' EXISTE!
    garantia_status = df_equipamentos['em_garantia'].unique()
    garantia_selecionada = st.sidebar.multiselect("Filtrar por Garantia:", options=garantia_status, default=garantia_status)

    # Aplicação dos filtros
    df_filtrado = df_equipamentos[
        df_equipamentos['sistema_alocado'].isin(sistemas_selecionados) &
        df_equipamentos['em_garantia'].isin(garantia_selecionada)
    ]

    # --- Exibição da Tabela ---
    st.dataframe(
        df_filtrado,
        hide_index=True,
        width='stretch',
        column_config={
            "id": "ID",
            "numero_serie": "Nº de Série",
            "descricao": "Descrição",
            "modelo": "Modelo",
            "status": "Status",
            "sistema_alocado": "Sistema",
            "data_aquisicao": st.column_config.DateColumn("Data Aquisição", format="DD/MM/YYYY"),
            "custo_aquisicao": st.column_config.NumberColumn("Custo (R$)", format="R$ %.2f"),
            "inicio_garantia": st.column_config.DateColumn("Início Garantia", format="DD/MM/YYYY"),
            "fim_garantia": st.column_config.DateColumn("Fim Garantia", format="DD/MM/YYYY"),
            "em_garantia": "Em Garantia?"
        }
    )

else:
    st.warning("⚠️ Nenhum equipamento cadastrado no sistema ainda.")


