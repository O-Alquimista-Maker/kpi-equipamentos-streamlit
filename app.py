# kpi_equipamentos/app.py

import streamlit as st

st.set_page_config(
    page_title="Home | KPI de Equipamentos",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Sistema de Gestão de KPIs para Equipamentos Analíticos")
st.markdown("---")

st.markdown("Bem-vindo! Esta ferramenta foi desenvolvida para centralizar e analisar informações sobre o ciclo de vida de equipamentos analíticos.")

st.header("Funcionalidades Principais")
col1, col2 = st.columns(2)

with col1:
    st.subheader("📠 Cadastro e Visualização")
    st.markdown("""
        - **Cadastro de Equipamentos:** Registre novos equipamentos e seus custos de aquisição.
        - **Visualização de Equipamentos:** Veja e filtre a lista de ativos.
        - **Cadastro de Manutenções:** Registre eventos de manutenção para cada equipamento.
    """)

with col2:
    st.subheader("🚀 Dashboards de KPIs")
    st.markdown("""
        - **Visão Geral Financeira:** Métricas de custo total de aquisição, manutenção e TCO.
        - **Análise de Custos:** Visualize os custos de manutenção por equipamento ou por sistema.
        - **(Em breve) Análise de Tipos de Manutenção:** Compare custos de manutenções corretivas vs. preventivas.
    """)

st.info("Use o menu na barra lateral para navegar entre as páginas.")
