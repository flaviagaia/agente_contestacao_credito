from __future__ import annotations

import asyncio
import os
from typing import Any, Callable

from .tools import (
    assess_dispute_strength,
    build_customer_explanation,
    compliance_guardrail,
    get_dispute_profile,
    suggest_contestation_strategy,
)


try:
    from agents import Agent, Runner, function_tool  # type: ignore

    OPENAI_AGENTS_SDK_AVAILABLE = True
except Exception:
    Agent = Runner = function_tool = None
    OPENAI_AGENTS_SDK_AVAILABLE = False


def _wrap_tools_for_sdk() -> list[Any]:
    assert function_tool is not None

    def make_tool(fn: Callable[..., str]) -> Any:
        return function_tool(fn)

    return [
        make_tool(get_dispute_profile),
        make_tool(assess_dispute_strength),
        make_tool(build_customer_explanation),
        make_tool(suggest_contestation_strategy),
        make_tool(compliance_guardrail),
    ]


def build_openai_agent(model: str = "gpt-4.1-mini"):
    assert Agent is not None
    return Agent(
        name="credit_dispute_explainer_agent",
        model=model,
        instructions=(
            "Você é um agente de contestação de crédito. "
            "Explique o caso com clareza, use as tools antes de responder, "
            "não prometa ganho de causa e trate qualquer recomendação como orientação inicial."
        ),
        tools=_wrap_tools_for_sdk(),
    )


def run_fallback_agent(case_id: str, user_question: str) -> str:
    profile = get_dispute_profile(case_id)
    strength = assess_dispute_strength(case_id)
    explanation = build_customer_explanation(case_id)
    strategy = suggest_contestation_strategy(case_id)
    guardrail = compliance_guardrail(user_question)
    return (
        f"Pergunta do cliente: {user_question}\n\n"
        f"Perfil consultado:\n{profile}\n\n"
        f"Explicação do caso:\n{explanation}\n\n"
        f"Força da contestação:\n{strength}\n\n"
        f"Estratégia sugerida:\n{strategy}\n\n"
        f"{guardrail}"
    )


async def _run_sdk(case_id: str, user_question: str, model: str) -> str:
    assert Runner is not None
    agent = build_openai_agent(model=model)
    prompt = (
        f"case_id={case_id}. "
        f"Pergunta do cliente: {user_question}. "
        "Use as tools para explicar o caso, avaliar a força da contestação e sugerir próximos passos."
    )
    result = await Runner.run(agent, prompt)
    return result.final_output


def ask_dispute_agent(case_id: str, user_question: str, model: str = "gpt-4.1-mini") -> dict[str, Any]:
    if OPENAI_AGENTS_SDK_AVAILABLE and os.getenv("OPENAI_API_KEY"):
        answer = asyncio.run(_run_sdk(case_id=case_id, user_question=user_question, model=model))
        return {"runtime_mode": "openai_agents_sdk", "answer": answer}
    return {
        "runtime_mode": "deterministic_fallback",
        "answer": run_fallback_agent(case_id=case_id, user_question=user_question),
    }
