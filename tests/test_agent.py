from __future__ import annotations

import unittest

from src.agent import ask_dispute_agent
from src.tools import assess_dispute_strength, suggest_contestation_strategy


class CreditDisputeAgentTest(unittest.TestCase):
    def test_fallback_agent_returns_answer(self) -> None:
        result = ask_dispute_agent(
            case_id="DISP-1002",
            user_question="Explique meu caso e o que devo fazer.",
        )
        self.assertIn("runtime_mode", result)
        self.assertIn("answer", result)
        self.assertGreater(len(result["answer"]), 20)

    def test_strength_tool_returns_strength(self) -> None:
        output = assess_dispute_strength("DISP-1002")
        self.assertIn("força estimada", output.lower())

    def test_strategy_tool_returns_strategy(self) -> None:
        output = suggest_contestation_strategy("DISP-1003")
        self.assertIn("estratégia sugerida", output.lower())


if __name__ == "__main__":
    unittest.main()
