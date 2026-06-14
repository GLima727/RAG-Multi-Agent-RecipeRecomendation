from .agents.recipe_agent import RecipeAgent


def run_agent(
    preferences: str,
    ingredients: str,
    dietary_restrictions: list[str] | None = None,
) -> str:
    return RecipeAgent().run(preferences, ingredients, dietary_restrictions)
