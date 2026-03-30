from __future__ import annotations

from src.agent import ask_dispute_agent


def main() -> None:
    result = ask_dispute_agent(
        case_id="DISP-1002",
        user_question="Minha contestação tem chance de ser fortalecida? O que devo destacar?",
    )
    print("Agente Contestacao Credito")
    print("-------------------------------------")
    print(f"runtime_mode: {result['runtime_mode']}")
    print(result["answer"])


if __name__ == "__main__":
    main()
