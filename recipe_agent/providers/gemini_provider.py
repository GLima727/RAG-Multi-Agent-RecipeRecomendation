"""
providers/gemini_provider.py — Google Gemini via the google-genai SDK.
"""

import os

from ..config import MAX_TOOL_ROUNDS, SYSTEM_PROMPT
from ..tools import build_user_message, execute_tool, get_gemini_tools
from .base import BaseProvider


class GeminiProvider(BaseProvider):
    name = "gemini"
    model = "gemini-2.0-flash"
    api_key_env = "GEMINI_API_KEY"

    def run(self, preferences: str, ingredients: str) -> str:
        from google import genai
        from google.genai import types

        api_key = os.environ.get(self.api_key_env)
        if not api_key:
            raise EnvironmentError(f"Environment variable '{self.api_key_env}' is not set.")

        client = genai.Client(api_key=api_key)
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=get_gemini_tools(),
        )

        chat = client.chats.create(model=self.model, config=config)
        try:
            response = chat.send_message(build_user_message(preferences, ingredients))
        except Exception:
            return (
                "I couldn't find any recipes matching your request. "
                "Try different ingredients or broader preferences."
            )

        for _ in range(MAX_TOOL_ROUNDS):
            function_calls = [
                part.function_call
                for part in response.candidates[0].content.parts
                if part.function_call
            ]

            if not function_calls:
                return "".join(
                    part.text
                    for part in response.candidates[0].content.parts
                    if hasattr(part, "text") and part.text
                )

            tool_responses = [
                types.Part.from_function_response(
                    name=fc.name,
                    response={"result": execute_tool(fc.name, dict(fc.args))},
                )
                for fc in function_calls
            ]
            try:
                response = chat.send_message(tool_responses)
            except Exception:
                return (
                    "I couldn't find any recipes matching your request. "
                    "Try different ingredients or broader preferences."
                )

        return "Could not generate recommendations. Please try again."
