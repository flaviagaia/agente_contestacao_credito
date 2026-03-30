from __future__ import annotations

import streamlit as st

from src.agent import ask_dispute_agent
from src.sample_data import load_disputes


st.set_page_config(page_title="Agente de Contestação de Crédito", page_icon="📄", layout="wide")

st.title("Agente de Contestação de Crédito")
st.caption(
    "MVP com OpenAI Agents SDK para explicar eventos contestados, avaliar força do caso e orientar a próxima ação."
)

cases = load_disputes()

with st.sidebar:
    st.subheader("Configuração")
    selected_case = st.selectbox("Caso", cases["case_id"].tolist())
    question = st.text_area(
        "Pergunta do cliente",
        value="Quero entender se minha contestação tem força e qual o melhor próximo passo.",
        height=140,
    )
    run_button = st.button("Consultar agente")

selected_profile = cases.loc[cases["case_id"] == selected_case].iloc[0].to_dict()

metrics = st.columns(4)
metrics[0].metric("Cliente", selected_profile["customer_name"])
metrics[1].metric("Evento", selected_profile["credit_event_type"])
metrics[2].metric("Impacto no score", int(selected_profile["score_impact_points"]))
metrics[3].metric("Status", selected_profile["status"])

left, right = st.columns([1.15, 1.0])

with left:
    st.subheader("Caso consultado")
    st.json(selected_profile)

with right:
    st.subheader("Arquitetura do agente")
    st.markdown(
        """
        - `OpenAI Agents SDK Agent`: coordena a resposta final.
        - `get_dispute_profile`: recupera os dados do caso.
        - `assess_dispute_strength`: estima a força da contestação.
        - `build_customer_explanation`: explica o caso em linguagem acessível.
        - `suggest_contestation_strategy`: define a próxima ação operacional.
        - `compliance_guardrail`: limita promessas e reforça linguagem segura.
        """
    )

if run_button:
    result = ask_dispute_agent(selected_case, question)
    st.subheader("Resposta do agente")
    st.info(f"Modo de execução: {result['runtime_mode']}")
    st.write(result["answer"])
