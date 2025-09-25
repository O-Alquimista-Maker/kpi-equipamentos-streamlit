# kpi_equipamentos/pages/4_Dashboard_KPIs.py

import streamlit as st
import pandas as pd
import plotly.express as px
from database.database_manager import listar_manutencoes_df, listar_equipamentos_df
import datetime

st.set_page_config(page_title="Dashboard de KPIs", page_icon="📊", layout="wide")
st.title("📊 Dashboard de KPIs de Manutenção e Ativos")

# --- Carregamento de Dados ---
@st.cache_data
def carregar_dados():
    manutencoes = listar_manutencoes_df()
    equipamentos = listar_equipamentos_df()
    if not manutencoes.empty: manutencoes['data_manutencao'] = pd.to_datetime(manutencoes['data_manutencao'])
    if not equipamentos.empty: equipamentos['data_aquisicao'] = pd.to_datetime(equipamentos['data_aquisicao'])
    return manutencoes, equipamentos

df_manutencoes_original, df_equipamentos_original = carregar_dados()

# --- FILTROS DENTRO DE UM EXPANDER ---
with st.expander("⚙️ Filtros e Opções", expanded=False):
    datas_manutencao = df_manutencoes_original['data_manutencao'] if not df_manutencoes_original.empty else pd.Series(dtype='datetime64[ns]')
    datas_aquisicao = df_equipamentos_original['data_aquisicao'] if not df_equipamentos_original.empty else pd.Series(dtype='datetime64[ns]')
    todas_as_datas = pd.concat([datas_manutencao, datas_aquisicao])
    data_minima_geral = todas_as_datas.min().date() if not todas_as_datas.empty else datetime.date.today()
    data_maxima_geral = todas_as_datas.max().date() if not todas_as_datas.empty else datetime.date.today()

    col_data1, col_data2, col_sistema = st.columns([1, 1, 2])
    with col_data1: data_inicio = st.date_input("Data de Início", value=data_minima_geral, min_value=data_minima_geral, max_value=data_maxima_geral, format="DD/MM/YYYY")
    with col_data2: data_fim = st.date_input("Data de Fim", value=data_maxima_geral, min_value=data_minima_geral, max_value=data_maxima_geral, format="DD/MM/YYYY")
    
    with col_sistema:
        sistemas_unicos = sorted(df_equipamentos_original['sistema_alocado'].dropna().unique())
        if 'sistemas_selecionados' not in st.session_state: st.session_state.sistemas_selecionados = sistemas_unicos
        botoes_col1, botoes_col2 = st.columns(2)
        if botoes_col1.button("Selecionar Todos", use_container_width=True): st.session_state.sistemas_selecionados = sistemas_unicos; st.rerun()
        if botoes_col2.button("Limpar Seleção", use_container_width=True): st.session_state.sistemas_selecionados = []; st.rerun()
        sistemas_selecionados = st.multiselect("Filtrar por Sistema:", options=sistemas_unicos, key='sistemas_selecionados')

# --- Lógica de Filtragem ---
data_inicio_ts, data_fim_ts = pd.to_datetime(data_inicio), pd.to_datetime(data_fim)
df_manutencoes = df_manutencoes_original[(df_manutencoes_original['data_manutencao'] >= data_inicio_ts) & (df_manutencoes_original['data_manutencao'] <= data_fim_ts) & (df_manutencoes_original['sistema_alocado'].isin(sistemas_selecionados))]
df_equipamentos = df_equipamentos_original[(df_equipamentos_original['data_aquisicao'] >= data_inicio_ts) & (df_equipamentos_original['data_aquisicao'] <= data_fim_ts) & (df_equipamentos_original['sistema_alocado'].isin(sistemas_selecionados))]
equipamentos_por_sistema = df_equipamentos_original[df_equipamentos_original['sistema_alocado'].isin(sistemas_selecionados)]

# --- MÉTRICAS PRINCIPAIS ---
st.markdown("---")
st.header("KPIs Gerais (Filtro Aplicado)")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Custo Aquisição (Período)", f"R$ {df_equipamentos['custo_aquisicao'].sum():,.2f}")
col2.metric("Custo Manutenção (Período)", f"R$ {df_manutencoes['custo_manutencao'].sum():,.2f}")
status_counts = equipamentos_por_sistema['status'].value_counts()
col3.metric("Equip. Operacionais", int(status_counts.get('Operacional', 0)))
col4.metric("Equip. Em Manutenção", int(status_counts.get('Em Manutenção', 0)), delta=int(status_counts.get('Em Manutenção', 0)) if int(status_counts.get('Em Manutenção', 0)) > 0 else None, delta_color="inverse")

st.markdown("---")

# --- GRÁFICOS EM ABAS ---
if df_equipamentos_original.empty:
    st.warning("⚠️ Nenhum equipamento registrado no sistema.")
else:
    tab_op, tab_fin = st.tabs(["📈 Análise Operacional", "💰 Análise Financeira"])
    with tab_op:
        op_col1, op_col2 = st.columns(2)
        with op_col1:
            st.subheader("Distribuição de Status dos Ativos")
            status_df = status_counts.reset_index(); status_df.columns = ['status', 'contagem']
            fig_status = px.pie(status_df, names='status', values='contagem', hole=0.4, color_discrete_map={'Operacional': '#00CC96', 'Em Manutenção': '#FFA15A', 'Desativado': '#AB63FA'})
            fig_status.update_traces(textinfo='percent+label', textposition='outside'); fig_status.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_status, use_container_width=True)
        with op_col2:
            st.subheader("Tendência de Manutenções no Período")
            if not df_manutencoes.empty:
                df_tendencia = df_manutencoes.copy(); df_tendencia['mes_ano'] = df_tendencia['data_manutencao'].dt.strftime('%Y-%m')
                tendencia_mensal = df_tendencia.groupby('mes_ano').size().reset_index(name='contagem').sort_values(by='mes_ano')
                fig_tendencia = px.line(tendencia_mensal, x='mes_ano', y='contagem', markers=True, labels={'mes_ano': 'Mês', 'contagem': 'Nº de Manutenções'})
                fig_tendencia.update_traces(line=dict(color='#636EFA', width=3)); st.plotly_chart(fig_tendencia, use_container_width=True)
            else: st.info("Nenhuma manutenção no período para exibir tendência.")
    with tab_fin:
        fin_col1, fin_col2 = st.columns(2)
        with fin_col1:
            # --- CORREÇÃO APLICADA AQUI ---
            st.subheader("Custo Total de Propriedade (Período)")
            # Usando os dataframes JÁ FILTRADOS: df_equipamentos e df_manutencoes
            custo_aq = df_equipamentos.groupby('descricao')['custo_aquisicao'].sum().reset_index().rename(columns={'custo_aquisicao': 'Custo Aquisição'})
            custo_man = df_manutencoes.groupby('equipamento_descricao')['custo_manutencao'].sum().reset_index().rename(columns={'equipamento_descricao': 'descricao', 'custo_manutencao': 'Custo Manutenção'})
            
            if not custo_aq.empty or not custo_man.empty:
                df_tco = pd.merge(custo_aq, custo_man, on='descricao', how='outer').fillna(0)
                df_tco['TCO'] = df_tco['Custo Aquisição'] + df_tco['Custo Manutenção']
                df_tco_melted = df_tco.melt(id_vars='descricao', value_vars=['Custo Aquisição', 'Custo Manutenção'], var_name='Tipo de Custo', value_name='Custo')
                fig_tco = px.bar(df_tco_melted, x='descricao', y='Custo', color='Tipo de Custo', barmode='stack', color_discrete_map={'Custo Aquisição': '#00CC96', 'Custo Manutenção': '#EF553B'})
                st.plotly_chart(fig_tco, use_container_width=True)
            else:
                st.info("Nenhum custo de aquisição ou manutenção no período selecionado.")
        with fin_col2:
            st.subheader("Custos de Manutenção no Período")
            if not df_manutencoes.empty:
                visao_custo = st.radio("Analisar por:", ["Equipamento", "Sistema"], horizontal=True, key="radio_custo")
                grupo = 'equipamento_descricao' if visao_custo == "Equipamento" else 'sistema_alocado'
                df_agregado = df_manutencoes.groupby(grupo)['custo_manutencao'].sum().reset_index().rename(columns={grupo: 'Agrupador', 'custo_manutencao': 'Custo Total'}).sort_values(by='Custo Total', ascending=False)
                fig_custo = px.bar(df_agregado, x='Agrupador', y='Custo Total', text_auto='.2s', color='Agrupador')
                fig_custo.update_layout(xaxis_title=None, showlegend=False); st.plotly_chart(fig_custo, use_container_width=True)
            else: st.info("Nenhum custo de manutenção no período.")
