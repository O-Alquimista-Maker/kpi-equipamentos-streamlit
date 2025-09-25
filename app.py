# kpi_equipamentos/app.py

import streamlit as st

# --- Configuração da Página ---
# Define o título da aba, o ícone e o layout da página.
# Este deve ser o primeiro comando Streamlit no seu script.
# No topo do arquivo
st.set_page_config(
    page_title="KPI Equipamentos - Início",
    page_icon="🏠",  # MUDANÇA AQUI: de 📈 para 🏠
    layout="wide"
)

# --- Conteúdo da Página Principal ---

# Título principal da aplicação
st.title("📈 Plataforma de KPI de Equipamentos Analíticos")
st.markdown("---")

# Mensagem de boas-vindas e descrição do projeto
st.header("Bem-vindo(a) à plataforma central de gestão de ativos.")
st.write("""
Esta aplicação foi desenvolvida para centralizar e analisar os dados de equipamentos analíticos, 
desde a aquisição até a manutenção, fornecendo indicadores chave de desempenho (KPIs) 
para otimizar a gestão e os custos operacionais.
""")

st.info("Selecione uma página na barra lateral à esquerda para começar a navegar.")

st.subheader("Funcionalidades Disponíveis:")

# Usando colunas para descrever as funcionalidades de forma organizada
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown("##### 📝 Cadastros")
        st.write("""
        - **Cadastro de Equipamento:** Adicione novos ativos ao sistema.
        - **Cadastro de Manutenção:** Registre eventos de manutenção corretiva ou preventiva.
        """)

    with st.container(border=True):
        st.markdown("##### 🗂️ Gerenciamento")
        st.write("""
        - **Gerenciar Dados:** Edite ou exclua registros de equipamentos e manutenções de forma segura e controlada.
        """)

with col2:
    with st.container(border=True):
        st.markdown("##### 📊 Análise e KPIs")
        st.write("""
        - **Dashboard de KPIs:** Visualize os principais indicadores de custo, status e operação em um painel interativo.
        - **Detalhes do Equipamento:** Consulte um dossiê completo de qualquer ativo, incluindo seu histórico de manutenções e status de garantia.
        """)

st.markdown("---")
st.caption("Desenvolvido por 🧙‍♂️ Fabio Sena 🧙‍♂️ | Versão 1.1")

