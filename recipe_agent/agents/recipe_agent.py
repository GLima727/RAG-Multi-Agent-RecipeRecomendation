import os

from langchain.agents import create_agent
from langchain.agents.middleware import ModelCallLimitMiddleware
from langchain_groq import ChatGroq

from ..config import MAX_TOOL_ROUNDS, SYSTEM_PROMPT
from ..logger import get_logger
from ..tools import search_recipes

log = get_logger("agents.recipe")

MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
API_KEY_ENV = "GROQ_API_KEY"


def _build_user_message(
    preferences: str,
    ingredients: str,
    dietary_restrictions: list[str] | None = None,
) -> str:
    restrictions = dietary_restrictions or []
    restrictions_line = (
        f"Dietary restrictions: {', '.join(restrictions)}"
        if restrictions
        else "Dietary restrictions: none"
    )
    return (
        f"{restrictions_line}\n"
        f"Other preferences: {preferences}\n"
        f"Available ingredients: {ingredients}\n\n"
        "Please recommend the best recipes for me. "
        "Check each recipe's ingredients carefully to ensure it meets my dietary restrictions."
    )


class RecipeAgent:
    def __init__(self):
        api_key = os.environ.get(API_KEY_ENV)
        if not api_key:
            raise EnvironmentError(f"Environment variable '{API_KEY_ENV}' is not set.")

        llm = ChatGroq(api_key=api_key, model=MODEL)
        self._agent = create_agent(
            llm,
            tools=[search_recipes],
            system_prompt=SYSTEM_PROMPT,
            middleware=[ModelCallLimitMiddleware(run_limit=MAX_TOOL_ROUNDS)],
        )

    def run(
        self,
        preferences: str,
        ingredients: str,
        dietary_restrictions: list[str] | None = None,
    ) -> str:
        user_message = _build_user_message(preferences, ingredients, dietary_restrictions)
        log.debug("running recipe agent")
        result = self._agent.invoke({"messages": [{"role": "user", "content": user_message}]})
        return result["messages"][-1].content
