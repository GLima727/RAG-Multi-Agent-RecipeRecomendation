"""
providers/gemini_provider.py — Google Gemini via the google-generativeai SDK.

Uses a stateful ChatSession so multi-turn tool use stays clean; google.generativeai
is imported lazily to avoid a hard dependency when other providers are used.
"""

import os

from ..config import MAX_TOOL_ROUNDS, SYSTEM_PROMPT
from ..tools import build_user_message, execute_tool, get_gemini_tools
from .base import BaseProvider


class GeminiProvider(BaseProvider):
    name = "gemini"
    model = "gemini-1.5-flash"
    api_key_env = "GEMINI_API_KEY"

    def run(self, preferences: str, ingredients: str) -> str:
        import google.generativeai as genai

        api_key = os.environ.get(self.api_key_env)
        if not api_key:
            raise EnvironmentError(f"Environment variable '{self.api_key_env}' is not set.")

        genai.configure(api_key=api_key)

        gemini_model = genai.GenerativeModel(
            self.model,
            tools=get_gemini_tools(),
            system_instruction=SYSTEM_PROMPT,
        )
        chat = gemini_model.start_chat()
        response = chat.send_message(build_user_message(preferences, ingredients))

        for _ in range(MAX_TOOL_ROUNDS):
            function_calls = [p.function_call for p in response.parts if p.function_call.name]

            if not function_calls:
                return "".join(p.text for p in response.parts if hasattr(p, "text") and p.text)

            tool_responses = [
                genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(
                        name=fc.name,
                        response={"result": execute_tool(fc.name, dict(fc.args))},
                    )
                )
                for fc in function_calls
            ]
            response = chat.send_message(tool_responses)

        return "Could not generate recommendations. Please try again."
