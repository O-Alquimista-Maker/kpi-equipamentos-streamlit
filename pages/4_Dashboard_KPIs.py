# kpi_equipamentos/pages/4_Dashboard_KPIs.py

import streamlit as st
import pandas as pd
import plotly.express as px
from database.database_manager import listar_manutencoes_df, listar_equipamentos_df
import datetime

# --- Configuração e Carregamento de Dados ---
st.set_page_config(page_title="Dashboard de KPIs", page_icon="🚀", layout="wide")
st.title("🚀 Dashboard de KPIs de Manutenção e Ativos")
st.markdown("---")

@st.cache_data
def carregar_dados_manutencao():
    df = listar_manutencoes_df()
    if not df.empty:
        df['data_manutencao'] = pd.to_datetime(df['data_manutencao'])
    return df

@st.cache_data
def carregar_dados_equipamentos():
    df = listar_equipamentos_df()
    if not df.empty:
        df['data_aquisicao'] = pd.to_datetime(df['data_aquisicao'])
    return df

df_manutencoes_original = carregar_dados_manutencao()
df_equipamentos_original = carregar_dados_equipamentos()

# --- FILTROS GLOBAIS ---
st.header("Filtros Globais")

# Define as datas min/max ANTES das colunas
datas_manutencao = df_manutencoes_original['data_manutencao'] if not df_manutencoes_original.empty else pd.Series(dtype='datetime64[ns]')
datas_aquisicao = df_equipamentos_original['data_aquisicao'] if not df_equipamentos_original.empty else pd.Series(dtype='datetime64[ns]')
todas_as_datas = pd.concat([datas_manutencao, datas_aquisicao])

if not todas_as_datas.empty:
    data_minima_geral = todas_as_datas.min().date()
    data_maxima_geral = todas_as_datas.max().date()
else:
    data_minima_geral = datetime.date.today()
    data_maxima_geral = datetime.date.today()

# Cria as colunas para os filtros
col_data1, col_data2, col_sistema = st.columns([1, 1, 2])

with col_data1:
    data_inicio = st.date_input("Data de Início", value=data_minima_geral, min_value=data_minima_geral, max_value=data_maxima_geral, format="DD/MM/YYYY")
with col_data2:
    data_fim = st.date_input("Data de Fim", value=data_maxima_geral, min_value=data_minima_geral, max_value=data_maxima_geral, format="DD/MM/YYYY")

with col_sistema:
    sistemas_unicos = sorted(df_equipamentos_original['sistema_alocado'].dropna().unique())
    
    # Inicializa o estado da sessão para o filtro
    if 'sistemas_selecionados' not in st.session_state:
        st.session_state.sistemas_selecionados = sistemas_unicos

    # Botões para controle rápido
    botoes_col1, botoes_col2 = st.columns(2)
    if botoes_col1.button("Selecionar Todos", use_container_width=True):
        st.session_state.sistemas_selecionados = sistemas_unicos
        st.rerun()
    if botoes_col2.button("Limpar Seleção", use_container_width=True):
        st.session_state.sistemas_selecionados = []
        st.rerun()

    # O multiselect usa 'key' e não 'default' para seguir as melhores práticas
    sistemas_selecionados = st.multiselect(
        "Filtrar por Sistema:",
        options=sistemas_unicos,
        key='sistemas_selecionados'
    )

# --- Lógica de Filtragem ---
data_inicio_ts = pd.to_datetime(data_inicio)
data_fim_ts = pd.to_datetime(data_fim)
df_manutencoes_filtrado_data = df_manutencoes_original[(df_manutencoes_original['data_manutencao'] >= data_inicio_ts) & (df_manutencoes_original['data_manutencao'] <= data_fim_ts)]
df_equipamentos_filtrado_data = df_equipamentos_original[(df_equipamentos_original['data_aquisicao'] >= data_inicio_ts) & (df_equipamentos_original['data_aquisicao'] <= data_fim_ts)]

df_manutencoes = df_manutencoes_filtrado_data[df_manutencoes_filtrado_data['sistema_alocado'].isin(sistemas_selecionados)]
df_equipamentos = df_equipamentos_filtrado_data[df_equipamentos_filtrado_data['sistema_alocado'].isin(sistemas_selecionados)]

st.markdown("---")

# --- Visão Geral com Novas Métricas ---
st.header("Visão Geral (Filtro Aplicado)")

# KPIs Financeiros
custo_aquisicao_periodo = df_equipamentos['custo_aquisicao'].sum()
custo_manutencao_periodo = df_manutencoes['custo_manutencao'].sum()
tco_periodo = custo_aquisicao_periodo + custo_manutencao_periodo

# KPIs Operacionais de Status
equipamentos_por_sistema = df_equipamentos_original[df_equipamentos_original['sistema_alocado'].isin(sistemas_selecionados)]
status_counts = equipamentos_por_sistema['status'].value_counts()

# Convertendo os valores de numpy.int64 para int nativo do Python
operacionais = int(status_counts.get('Operacional', 0))
em_manutencao = int(status_counts.get('Em Manutenção', 0))
desativados = int(status_counts.get('Desativado', 0))

# Layout das Métricas
st.subheader("Análise Financeira")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Custo de Aquisição (Período)", value=f"R$ {custo_aquisicao_periodo:,.2f}")
with col2:
    st.metric(label="Custo de Manutenção (Período)", value=f"R$ {custo_manutencao_periodo:,.2f}")
with col3:
    st.metric(label="Custo Total (TCO) no Período", value=f"R$ {tco_periodo:,.2f}")

st.subheader("Análise Operacional de Status (Sistemas Selecionados)")
col4, col5, col6 = st.columns(3)
with col4:
    st.metric(label="Equipamentos Operacionais", value=operacionais)
with col5:
    st.metric(label="Equipamentos Em Manutenção", value=em_manutencao, delta=em_manutencao if em_manutencao > 0 else None, delta_color="inverse")
with col6:
    st.metric(label="Equipamentos Desativados", value=desativados)

st.markdown("---")

# --- GRÁFICOS ---
if df_equipamentos_original.empty:
    st.warning("⚠️ Nenhum equipamento registrado no sistema. Cadastre um equipamento para começar.")
else:
    # --- Seção de Análise Operacional ---
    st.header("Análise Operacional")
    op_col1, op_col2 = st.columns(2)

    with op_col1:
        st.subheader("Distribuição de Status dos Ativos")
        status_df = status_counts.reset_index()
        status_df.columns = ['status', 'contagem']
        fig_status = px.pie(status_df, names='status', values='contagem', title='Status dos Equipamentos (Sistemas Selecionados)', hole=0.4, color_discrete_map={'Operacional': '#00CC96', 'Em Manutenção': '#FFA15A', 'Desativado': '#AB63FA'})
        fig_status.update_traces(textinfo='percent+label', textposition='outside')
        st.plotly_chart(fig_status, use_container_width=True)

    with op_col2:
        st.subheader("Tendência de Manutenções no Período")
        if not df_manutencoes.empty:
            df_tendencia = df_manutencoes.copy()
            df_tendencia['mes_ano'] = df_tendencia['data_manutencao'].dt.strftime('%Y-%m')
            tendencia_mensal = df_tendencia.groupby('mes_ano').size().reset_index(name='contagem')
            tendencia_mensal = tendencia_mensal.sort_values(by='mes_ano')
            fig_tendencia = px.line(tendencia_mensal, x='mes_ano', y='contagem', title='Número de Manutenções por Mês', markers=True)
            fig_tendencia.update_traces(line=dict(color='#636EFA', width=3))
            st.plotly_chart(fig_tendencia, use_container_width=True)
        else:
            st.info("Nenhuma manutenção no período para exibir tendência.")

    st.markdown("---")

    # --- Seção de Análise Financeira ---
    st.header("Análise Financeira Detalhada")
    fin_col1, fin_col2 = st.columns(2)

    with fin_col1:
        st.subheader("Custo Total de Propriedade (Geral)")
        custo_aq_agregado = df_equipamentos_original.groupby('descricao')['custo_aquisicao'].sum().reset_index().rename(columns={'custo_aquisicao': 'Custo Aquisição'})
        custo_man_agregado = df_manutencoes_original.groupby('equipamento_descricao')['custo_manutencao'].sum().reset_index().rename(columns={'equipamento_descricao': 'descricao', 'custo_manutencao': 'Custo Manutenção'})
        df_tco = pd.merge(custo_aq_agregado, custo_man_agregado, on='descricao', how='outer').fillna(0)
        df_tco['TCO'] = df_tco['Custo Aquisição'] + df_tco['Custo Manutenção']
        df_tco = df_tco.sort_values(by='TCO', ascending=False)
        df_tco_melted = df_tco.melt(id_vars='descricao', value_vars=['Custo Aquisição', 'Custo Manutenção'], var_name='Tipo de Custo', value_name='Custo')
        fig_tco = px.bar(df_tco_melted, x='descricao', y='Custo', color='Tipo de Custo', title='TCO por Equipamento', barmode='stack', color_discrete_map={'Custo Aquisição': '#00CC96', 'Custo Manutenção': '#EF553B'})
        st.plotly_chart(fig_tco, use_container_width=True)

    with fin_col2:
        st.subheader("Custos de Manutenção no Período")
        if not df_manutencoes.empty:
            visao_custo = st.radio("Analisar custos por:", options=["Equipamento", "Sistema"], horizontal=True, key="radio_custo")
            if visao_custo == "Equipamento":
                df_agregado = df_manutencoes.groupby('equipamento_descricao')['custo_manutencao'].sum().reset_index()
                df_agregado = df_agregado.rename(columns={'equipamento_descricao': 'Agrupador', 'custo_manutencao': 'Custo Total'})
            else:
                df_agregado = df_manutencoes.groupby('sistema_alocado')['custo_manutencao'].sum().reset_index()
                df_agregado = df_agregado.rename(columns={'sistema_alocado': 'Agrupador', 'custo_manutencao': 'Custo Total'})
            df_agregado = df_agregado.sort_values(by='Custo Total', ascending=False)
            fig_custo = px.bar(df_agregado, x='Agrupador', y='Custo Total', text_auto='.2s', color='Agrupador')
            fig_custo.update_layout(xaxis_title=None, showlegend=False)
            st.plotly_chart(fig_custo, use_container_width=True)
        else:
            st.info("Nenhum custo de manutenção no período para exibir o gráfico.")


