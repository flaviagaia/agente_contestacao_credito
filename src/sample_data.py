from __future__ import annotations

from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError


RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
DISPUTES_PATH = RAW_DIR / "credit_disputes.csv"


SAMPLE_DISPUTES = [
    {
        "case_id": "DISP-1001",
        "customer_name": "Ana Souza",
        "credit_event_type": "late_payment",
        "disputed_reason": "Cliente informa que a fatura foi quitada antes do vencimento, mas o atraso foi registrado.",
        "amount_brl": 820.0,
        "days_past_due": 0,
        "score_impact_points": 18,
        "supporting_documents": "comprovante_pagamento, extrato_bancario",
        "status": "under_review",
        "issuer_response_history": "Sem resposta formal ainda.",
    },
    {
        "case_id": "DISP-1002",
        "customer_name": "Bruno Lima",
        "credit_event_type": "negative_record",
        "disputed_reason": "Cliente alega que a dívida já foi renegociada e quitada, mas a negativação continua ativa.",
        "amount_brl": 3400.0,
        "days_past_due": 0,
        "score_impact_points": 52,
        "supporting_documents": "termo_quitacao, comprovante_transferencia",
        "status": "under_review",
        "issuer_response_history": "Atendimento anterior respondeu genericamente sem revisar os anexos.",
    },
    {
        "case_id": "DISP-1003",
        "customer_name": "Carla Mendes",
        "credit_event_type": "hard_inquiry",
        "disputed_reason": "Cliente não reconhece consulta ao crédito feita por instituição com a qual afirma não ter relação.",
        "amount_brl": 0.0,
        "days_past_due": 0,
        "score_impact_points": 11,
        "supporting_documents": "declaracao_cliente, print_app_credito",
        "status": "under_review",
        "issuer_response_history": "Há apenas protocolo de abertura.",
    },
]


def ensure_sample_data() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    rebuild = not DISPUTES_PATH.exists()
    if DISPUTES_PATH.exists() and DISPUTES_PATH.stat().st_size == 0:
        rebuild = True
    if DISPUTES_PATH.exists() and not rebuild:
        try:
            preview = pd.read_csv(DISPUTES_PATH)
            if preview.empty or "case_id" not in preview.columns:
                rebuild = True
        except EmptyDataError:
            rebuild = True
    if rebuild:
        pd.DataFrame(SAMPLE_DISPUTES).to_csv(DISPUTES_PATH, index=False)


def load_disputes() -> pd.DataFrame:
    ensure_sample_data()
    return pd.read_csv(DISPUTES_PATH)
