# kpi_equipamentos/Início.py

import streamlit as st
from PIL import Image

# --- Configuração INICIAL da Página ---
# Deve ser o primeiro comando para funcionar corretamente na tela de login
st.set_page_config(
    page_title="KPI Equipamentos",
    page_icon="assets/logo.png",
    layout="centered" # Começa centralizado para a tela de login
)

# ==============================================================================
# --- LÓGICA DE AUTENTICAÇÃO (VERSÃO FINAL E ROBUSTA) ---
# ==============================================================================

# Carrega a senha mestra dos segredos para a sessão UMA VEZ.
# Isso evita o problema de "corrida" com o on_change.
if "master_password" not in st.session_state:
    try:
        st.session_state.master_password = st.secrets["app_auth"]["master_password"]
    except (KeyError, FileNotFoundError, st.errors.StreamlitAPIException):
        # Se não encontrar nos segredos (localmente), define uma senha vazia.
        # Isso evita que a aplicação local quebre.
        st.session_state.master_password = "" 

def check_password():
    """Verifica a senha digitada contra a senha mestra guardada na sessão."""
    password_digitada = st.session_state.get("password", "")
    
    # Compara com a senha que já está na memória da sessão.
    if password_digitada == st.session_state.master_password:
        st.session_state["password_correct"] = True
        # Limpa a senha digitada por segurança
        if "password" in st.session_state:
            del st.session_state["password"]
    else:
        st.session_state["password_correct"] = False

# Se a senha ainda não foi verificada, mostra o formulário de login
if st.session_state.get("password_correct", False) == False:
    st.title("🔐 Acesso Restrito")
    st.write("Esta aplicação é protegida. Por favor, insira a senha de acesso.")
    
    st.text_input(
        "Senha:", 
        type="password", 
        on_change=check_password, 
        key="password"
    )
    
    # Mensagem de erro se a tentativa falhou
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        # Verifica se a senha mestra está vazia (problema de configuração)
        if not st.session_state.master_password:
            st.error("Erro de configuração: Senha mestra não encontrada nos segredos.")
        else:
            # Não mostra o erro na primeira vez que a página carrega
            if "password" in st.session_state:
                st.error("Senha incorreta. Tente novamente.")
            
    st.stop() # Para a execução aqui

# --- SE A SENHA ESTIVER CORRETA, A APLICAÇÃO CONTINUA DAQUI PARA BAIXO ---
# ==============================================================================
# --- SEU CÓDIGO ORIGINAL COMEÇA AQUI ---
# ==============================================================================

# RECONFIGURA a página para o layout principal
st.set_page_config(
    page_title="KPI Equipamentos - Início",
    page_icon="🏠",
    layout="wide"
)

# Adiciona o logo no topo da barra lateral
try:
    logo = Image.open("assets/logo.png")
    st.sidebar.image(logo, use_container_width=True)
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

st.caption("Desenvolvido por 🧙‍♂️ Fabio Sena 🧙‍♂️ | Versão 1.3") # Versão atualizada!
