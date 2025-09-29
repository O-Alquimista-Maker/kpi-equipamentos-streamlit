# kpi_equipamentos/Início.py

import streamlit as st
from PIL import Image

# ==============================================================================
# --- LÓGICA DE AUTENTICAÇÃO (ADICIONADA AQUI) ---
# ==============================================================================

def check_password():
    """Retorna True se a senha estiver correta, False caso contrário."""
    try:
        # Pega a senha do formulário
        password = st.session_state["password"]
        
        # Compara com a senha mestra guardada nos segredos
        if password == st.secrets["app_auth"]["master_password"]:
            st.session_state["password_correct"] = True
            # Deleta a senha da memória da sessão por segurança
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False
    except KeyError:
        # Isso acontece se a seção 'app_auth' ou 'master_password' não estiver nos segredos
        st.session_state["password_correct"] = False

# Se a senha ainda não foi verificada, mostra o formulário de login
if "password_correct" not in st.session_state or not st.session_state["password_correct"]:
    # Usa uma configuração de página simples para a tela de login
    st.set_page_config(page_title="Login", layout="centered")
    st.title("🔐 Acesso Restrito")
    st.write("Esta aplicação é protegida. Por favor, insira a senha de acesso.")
    
    st.text_input(
        "Senha:", 
        type="password", 
        on_change=check_password, 
        key="password"
    )
    
    # Mostra mensagem de erro se a tentativa falhou
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("Senha incorreta. Tente novamente.")
    
    # Para a execução do script aqui, não mostrando o resto da página
    st.stop()

# --- SE A SENHA ESTIVER CORRETA, A APLICAÇÃO CONTINUA DAQUI PARA BAIXO ---
# ==============================================================================
# --- SEU CÓDIGO ORIGINAL COMEÇA AQUI (SEM MODIFICAÇÕES) ---
# ==============================================================================

# --- Configuração da Página ---
st.set_page_config(
    page_title="KPI Equipamentos - Início",
    page_icon="🏠",
    layout="wide"
)

# Adiciona o logo no topo da barra lateral
try:
    logo = Image.open("assets/logo.png")
    st.sidebar.image(logo, width='stretch') # Corrigido para o parâmetro mais recente
except FileNotFoundError:
    st.sidebar.error("Logo não encontrado. Verifique o caminho 'assets/logo.png'.")

st.sidebar.markdown("---")
st.sidebar.header("Navegação")

# --- Conteúdo da Página Principal ---
st.title("📈 Plataforma de KPI de Equipamentos Analíticos")
st.markdown("---")

st.header("Bem-vindo(a) à plataforma central de gestão de ativos.")
st.write("""
Esta aplicação foi desenvolvida para centralizar e analisar os dados de equipamentos analíticos, 
desde a aquisição até a manutenção, fornecendo indicadores chave de desempenho (KPIs) 
para otimizar a gestão e os custos operacionais.
""")

st.info("Selecione uma página na barra lateral à esquerda para começar a navegar.")

st.subheader("Funcionalidades Disponíveis:")

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

# Botão de Recarregar Dados na barra lateral
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Recarregar Dados"):
    st.cache_data.clear()
    st.toast("Dados recarregados com sucesso!", icon="✅")
    st.rerun()

st.caption("Desenvolvido por 🧙‍♂️ Fabio Sena 🧙‍♂️ | Versão 1.2") # Sugestão: atualizar a versão

