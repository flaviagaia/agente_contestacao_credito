from __future__ import annotations

import json
from typing import Any

from .sample_data import load_disputes


EVENT_TYPE_LABELS = {
    "negative_record": "registro negativo",
    "late_payment": "pagamento em atraso",
    "hard_inquiry": "consulta ao crédito não reconhecida",
}

STATUS_LABELS = {
    "under_review": "em análise",
}


def _get_case(case_id: str) -> dict[str, Any]:
    disputes = load_disputes()
    row = disputes.loc[disputes["case_id"] == case_id]
    if row.empty:
        raise ValueError(f"Caso '{case_id}' não encontrado.")
    return row.iloc[0].to_dict()


def _localized_case(case: dict[str, Any]) -> dict[str, Any]:
    localized = dict(case)
    localized["credit_event_type"] = EVENT_TYPE_LABELS.get(
        str(case["credit_event_type"]),
        str(case["credit_event_type"]),
    )
    localized["status"] = STATUS_LABELS.get(str(case["status"]), str(case["status"]))
    return localized


def get_dispute_profile(case_id: str) -> str:
    """Return the structured dispute profile for a case."""
    return json.dumps(_localized_case(_get_case(case_id)), ensure_ascii=False, indent=2)


def assess_dispute_strength(case_id: str) -> str:
    """Assess the strength of a credit dispute based on internal demo rules."""
    case = _localized_case(_get_case(case_id))
    documents = str(case["supporting_documents"]).split(",")
    score_impact = int(case["score_impact_points"])
    history = str(case["issuer_response_history"]).lower()

    strength = "moderada"
    reasons = []

    if len(documents) >= 2:
        reasons.append("há mais de um documento de suporte")
    if score_impact >= 40:
        reasons.append("o impacto no score é material")
    if "genericamente" in history or "sem resposta" in history:
        reasons.append("o histórico de resposta anterior sugere revisão superficial")

    if len(reasons) >= 3:
        strength = "alta"
    elif len(reasons) == 1:
        strength = "baixa"

    return (
        f"A força estimada da contestação é {strength}. "
        f"Justificativas observadas: {', '.join(reasons) if reasons else 'pouca evidência complementar no caso atual'}."
    )


def build_customer_explanation(case_id: str) -> str:
    """Build a customer-facing explanation of the dispute status."""
    case = _localized_case(_get_case(case_id))
    return (
        f"O caso {case_id} está {case['status']} e envolve o evento '{case['credit_event_type']}'. "
        f"O cliente reportou: {case['disputed_reason']} "
        f"Os anexos identificados foram: {case['supporting_documents']}. "
        f"O impacto estimado no score foi de {int(case['score_impact_points'])} pontos."
    )


def suggest_contestation_strategy(case_id: str) -> str:
    """Suggest the next operational strategy for the credit dispute."""
    case = _get_case(case_id)
    event_type = case["credit_event_type"]

    if event_type == "negative_record":
        return (
            "Estratégia sugerida: priorizar pedido formal de baixa imediata do registro, "
            "anexar termo de quitação e reforçar impacto reputacional e financeiro do apontamento indevido."
        )
    if event_type == "late_payment":
        return (
            "Estratégia sugerida: comparar comprovante de pagamento com a linha do tempo do vencimento "
            "e solicitar correção cadastral do apontamento de atraso."
        )
    return (
        "Estratégia sugerida: contestar a origem do evento, pedir trilha de auditoria da consulta e "
        "registrar que o cliente não reconhece a operação."
    )


def compliance_guardrail(topic: str) -> str:
    """Return compliance guidance for dispute-answering behavior."""
    return (
        "Diretriz de compliance: manter linguagem informativa, não prometer reversão automática, "
        "não afirmar direito garantido sem análise documental e deixar claro que a resposta é uma orientação inicial. "
        f"Tópico: {topic}."
    )
