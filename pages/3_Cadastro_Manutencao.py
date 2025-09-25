# kpi_equipamentos/pages/3_Cadastro_Manutencao.py

import streamlit as st
import pandas as pd
from database.database_manager import adicionar_manutencao, listar_equipamentos_df
import datetime

# --- Configuração da Página ---
st.set_page_config(
    page_title="Cadastro de Manutenção",
    page_icon="🛠️", # MUDANÇA AQUI
    layout="wide"
)

st.title("🛠️ Registro de Manutenção") # MUDANÇA AQUI

@st.cache_data
def carregar_equipamentos():
    df = listar_equipamentos_df()
    if not df.empty:
        df['display_name'] = df['descricao'] + " (S/N: " + df['numero_serie'] + ")"
    return df

df_equipamentos = carregar_equipamentos()

if df_equipamentos.empty:
    st.error("⚠️ Nenhum equipamento cadastrado. Cadastre um antes de registrar uma manutenção.")
else:
    with st.form("registro_manutencao_form", clear_on_submit=True):
        st.subheader("Selecione o Equipamento e os Detalhes")

        equipamento_selecionado_display = st.selectbox(
            "Equipamento*", options=df_equipamentos['display_name'],
            index=None, placeholder="Selecione o equipamento..."
        )

        col1, col2 = st.columns(2)
        with col1:
            data_manutencao = st.date_input("Data da Manutenção*", value=datetime.date.today(), format="DD/MM/YYYY")
            tipo_manutencao = st.selectbox("Tipo de Manutenção*", options=["Corretiva", "Preventiva"], index=None)
        with col2:
            custo_manutencao = st.number_input("Custo da Manutenção (R$)", min_value=0.0, value=0.0, format="%.2f")
        
        motivo_manutencao = st.text_area("Descrição/Motivo da Manutenção*")

        st.markdown("---")
        submitted = st.form_submit_button("✔️ Registrar Manutenção")

        if submitted:
            if not all([equipamento_selecionado_display, data_manutencao, tipo_manutencao, motivo_manutencao]):
                st.warning("Por favor, preencha todos os campos obrigatórios (*).")
            else:
                equipamento_id = df_equipamentos[df_equipamentos['display_name'] == equipamento_selecionado_display]['id'].iloc[0]
                
                success = adicionar_manutencao(
                    equipamento_id=int(equipamento_id),
                    data_manutencao=data_manutencao.isoformat(),
                    motivo_manutencao=str(motivo_manutencao),
                    tipo_manutencao=str(tipo_manutencao),
                    custo_manutencao=float(custo_manutencao)
                )

                if success:
                    st.success(f"Manutenção para '{equipamento_selecionado_display}' registrada!")
                    st.cache_data.clear()
                else:
                    st.error("❌ Ocorreu um erro ao registrar a manutenção.")
