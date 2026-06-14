"""
app.py — Streamlit frontend for the Recipe Recommendation Agent.

Usage:
    streamlit run app.py
"""

import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from recipe_agent import run_agent
from recipe_agent.agents.recipe_agent import API_KEY_ENV, MODEL
from recipe_agent.config import CHROMA_DB_PATH

st.set_page_config(
    page_title="Recipe Recommendation Agent",
    page_icon="🍽️",
    layout="centered",
)

st.title("Recipe Recommendation Agent")
st.caption("Powered by RAG over RecipeNLG")

DIETARY_OPTIONS = [
    "Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free",
    "Nut-Free", "Egg-Free", "Low-Carb", "Keto",
]

if not (os.path.isdir(CHROMA_DB_PATH) and any(os.scandir(CHROMA_DB_PATH))):
    st.error(
        "ChromaDB index not found. "
        "Run `python ingest.py` first to build the recipe index."
    )
    st.stop()

with st.sidebar:
    st.header("Settings")

    api_key_present = bool(os.environ.get(API_KEY_ENV))

    if api_key_present:
        st.success(f"`{API_KEY_ENV}` loaded")
    else:
        st.warning(f"`{API_KEY_ENV}` not set")
        manual_key = st.text_input(f"Enter {API_KEY_ENV}", type="password", key="manual_key")
        if manual_key:
            os.environ[API_KEY_ENV] = manual_key
            api_key_present = True

    st.divider()
    st.caption(f"Model: **{MODEL}**")

with st.form("query_form"):
    selected_restrictions = st.pills(
        "Dietary restrictions",
        options=DIETARY_OPTIONS,
        selection_mode="multi",
        default=None,
        help="Select one or more restrictions — recipes will be filtered accordingly.",
    )
    ingredients = st.text_area(
        "Available ingredients",
        placeholder="e.g. eggs, spinach, garlic, olive oil",
        height=100,
    )
    submitted = st.form_submit_button("Find Recipes", use_container_width=True)

if submitted:
    if not api_key_present:
        st.error(f"Set `{API_KEY_ENV}` before running the agent.")
        st.stop()

    restrictions = [r.lower() for r in (selected_restrictions or [])]
    ingr = ingredients.strip() or "pantry staples"

    with st.spinner("Agent is thinking…"):
        try:
            result = run_agent(
                preferences="no additional preferences",
                ingredients=ingr,
                dietary_restrictions=restrictions or None,
            )
        except Exception as exc:
            st.error(f"Error: {exc}")
            st.stop()

    st.divider()
    st.subheader("Recommendations")
    st.markdown(result)
