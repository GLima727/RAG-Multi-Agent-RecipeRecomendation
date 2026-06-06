"""
providers/openai_provider.py — OpenAI and Groq via the OpenAI-compatible API.

GroqProvider subclasses OpenAIProvider and overrides only the three class
attributes; the agentic loop is identical for both.
"""

import json
import os

from ..config import MAX_TOOL_ROUNDS, SYSTEM_PROMPT
from ..tools import OPENAI_TOOLS, build_user_message, execute_tool
from .base import BaseProvider


class OpenAIProvider(BaseProvider):
    name = "openai"
    model = "gpt-4o-mini"
    api_key_env = "OPENAI_API_KEY"
    base_url: str | None = None   # None → standard OpenAI endpoint

    def run(self, preferences: str, ingredients: str) -> str:
        from openai import OpenAI

        api_key = os.environ.get(self.api_key_env)
        if not api_key:
            raise EnvironmentError(f"Environment variable '{self.api_key_env}' is not set.")

        client = OpenAI(api_key=api_key, base_url=self.base_url)
        messages: list = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_message(preferences, ingredients)},
        ]

        for _ in range(MAX_TOOL_ROUNDS):
            response = client.chat.completions.create(
                model=self.model,
                tools=OPENAI_TOOLS,
                messages=messages,
            )
            choice = response.choices[0]
            msg = choice.message

            # Serialise assistant turn to a plain dict for the next API call.
            assistant_entry: dict = {"role": "assistant", "content": msg.content}
            if msg.tool_calls:
                assistant_entry["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                    }
                    for tc in msg.tool_calls
                ]
            messages.append(assistant_entry)

            if choice.finish_reason == "stop":
                return msg.content or ""

            if choice.finish_reason == "tool_calls" and msg.tool_calls:
                for tc in msg.tool_calls:
                    result = execute_tool(tc.function.name, json.loads(tc.function.arguments))
                    messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
            else:
                return msg.content or ""

        return "Could not generate recommendations. Please try again."


class GroqProvider(OpenAIProvider):
    name = "groq"
    model = "llama-3.3-70b-versatile"
    api_key_env = "GROQ_API_KEY"
    base_url = "https://api.groq.com/openai/v1"
