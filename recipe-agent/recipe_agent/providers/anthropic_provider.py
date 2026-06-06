"""
providers/anthropic_provider.py — Claude via the Anthropic Python SDK.
"""

import anthropic

from ..config import MAX_TOOL_ROUNDS, SYSTEM_PROMPT
from ..tools import ANTHROPIC_TOOLS, build_user_message, execute_tool
from .base import BaseProvider


class AnthropicProvider(BaseProvider):
    name = "anthropic"
    model = "claude-sonnet-4-20250514"
    api_key_env = "ANTHROPIC_API_KEY"

    def run(self, preferences: str, ingredients: str) -> str:
        client = anthropic.Anthropic()
        messages: list = [{"role": "user", "content": build_user_message(preferences, ingredients)}]

        for _ in range(MAX_TOOL_ROUNDS):
            response = client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=ANTHROPIC_TOOLS,
                messages=messages,
            )
            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "end_turn":
                return next((b.text for b in response.content if hasattr(b, "text")), "")

            if response.stop_reason == "tool_use":
                tool_calls = [b for b in response.content if b.type == "tool_use"]
                if not tool_calls:
                    break
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tc.id,
                            "content": execute_tool(tc.name, tc.input),
                        }
                        for tc in tool_calls
                    ],
                })

        return "Could not generate recommendations. Please try again."
