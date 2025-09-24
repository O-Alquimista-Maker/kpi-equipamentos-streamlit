# kpi_equipamentos/pages/1_Cadastro_Equipamento.py

import streamlit as st
from database.database_manager import adicionar_equipamento
import datetime

st.set_page_config(page_title="Cadastro de Equipamentos", page_icon="📠")
st.title("📠 Cadastro de Novos Equipamentos")
st.markdown("---")

with st.form("cadastro_equipamento_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Informações Básicas")
        numero_serie = st.text_input("Número de Série*", help="O identificador único do equipamento.")
        descricao = st.text_input("Descrição do Equipamento*", help="Ex: Cromatógrafo a Gás.")
        modelo = st.text_input("Modelo")
        sistema_alocado = st.text_input("Sistema Alocado", help="Ex: Cromatografia, Genômica.")
    with col2:
        st.subheader("Aquisição e Garantia")
        custo_aquisicao = st.number_input("Custo de Aquisição (R$)", min_value=0.0, value=0.0, format="%.2f")
        data_aquisicao = st.date_input("Data de Aquisição", value=None, format="DD/MM/YYYY")
        pedido_compra = st.text_input("Pedido de Compra (PC)")
        motivo_compra = st.text_area("Motivo da Compra")
        inicio_garantia = st.date_input("Início da Garantia", value=None, format="DD/MM/YYYY")
        fim_garantia = st.date_input("Fim da Garantia", value=None, format="DD/MM/YYYY")

    st.markdown("---")
    submitted = st.form_submit_button("✔️ Cadastrar Equipamento")

    if submitted:
        if not numero_serie or not descricao:
            st.warning("Por favor, preencha os campos obrigatórios (*).")
        else:
            success = adicionar_equipamento(
                numero_serie=numero_serie, descricao=descricao, modelo=modelo,
                sistema_alocado=sistema_alocado,
                custo_aquisicao=float(custo_aquisicao),
                data_aquisicao=data_aquisicao.isoformat() if data_aquisicao else None,
                pedido_compra=pedido_compra, motivo_compra=motivo_compra,
                inicio_garantia=inicio_garantia.isoformat() if inicio_garantia else None,
                fim_garantia=fim_garantia.isoformat() if fim_garantia else None
            )
            if success:
                st.success(f"Equipamento '{descricao}' (S/N: {numero_serie}) cadastrado!")
                st.cache_data.clear()
            else:
                st.error("❌ Erro ao cadastrar. Verifique se o número de série já não está em uso.")
