# kpi_equipamentos/pages/1_Cadastro_Equipamento.py

import streamlit as st
from database.database_manager import adicionar_equipamento
from PIL import Image
import datetime

# --- Configuração da Página ---
try:
    favicon = Image.open("assets/seu_logo.png")
    st.set_page_config(page_title="Cadastro de Equipamentos", page_icon=favicon)
except FileNotFoundError:
    st.set_page_config(page_title="Cadastro de Equipamentos", page_icon="🔬")

st.title("🔬 Cadastro de Novos Equipamentos")
st.markdown("---")

# --- Formulário de Cadastro ---
with st.form(key="cadastro_equipamento_form", clear_on_submit=True):
    st.subheader("Detalhes do Equipamento")
    
    col1, col2 = st.columns(2)
    with col1:
        numero_serie = st.text_input("Número de Série*", help="O número de série único do equipamento.")
        descricao = st.text_input("Descrição do Equipamento*", help="Ex: Cromatógrafo Líquido de Alta Eficiência")
        modelo = st.text_input("Modelo")
        status = st.selectbox("Status*", ["Operacional", "Em Manutenção", "Desativado"])
    
    with col2:
        sistema_alocado = st.text_input("Sistema Alocado", help="Ex: Cromatografia, Espectrometria de Massas")
        pedido_compra = st.text_input("Pedido de Compra (PC)") # <-- CAMPO NO FORMULÁRIO
        data_aquisicao = st.date_input("Data de Aquisição", value=None, format="DD/MM/YYYY")
        custo_aquisicao = st.number_input("Custo de Aquisição (R$)", min_value=0.0, format="%.2f")

    st.subheader("Informações de Garantia")
    col_garantia1, col_garantia2 = st.columns(2)
    with col_garantia1:
        inicio_garantia = st.date_input("Início da Garantia", value=None, format="DD/MM/YYYY")
    with col_garantia2:
        fim_garantia = st.date_input("Fim da Garantia", value=None, format="DD/MM/YYYY")

    st.markdown("---")
    submitted = st.form_submit_button("✔️ Cadastrar Equipamento")

    if submitted:
        if not numero_serie or not descricao:
            st.error("❌ Erro: Os campos 'Número de Série' e 'Descrição' são obrigatórios.")
        else:
            # GARANTIR QUE 'pedido_compra' ESTÁ SENDO PASSADO AQUI
            success = adicionar_equipamento(
                numero_serie=numero_serie, descricao=descricao, modelo=modelo,
                status=status, sistema_alocado=sistema_alocado,
                data_aquisicao=data_aquisicao.isoformat() if data_aquisicao else None,
                custo_aquisicao=custo_aquisicao,
                inicio_garantia=inicio_garantia.isoformat() if inicio_garantia else None,
                fim_garantia=fim_garantia.isoformat() if fim_garantia else None,
                pedido_compra=pedido_compra
            )
            
            if success:
                st.success("✅ Equipamento cadastrado com sucesso!")
                st.balloons()
            else:
                st.error("❌ Erro ao cadastrar o equipamento. Verifique se o número de série já existe.")
