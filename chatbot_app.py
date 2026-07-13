"""Capstone-style RAG chatbot - ask questions over your saved articles and
stock portfolio notes.

Run with:
    streamlit run chatbot_app.py
"""
from __future__ import annotations

import streamlit as st
from dotenv import load_dotenv

from deepseek_client import ask
from rag_store import RagStore

load_dotenv()

st.set_page_config(page_title="Portfolio Chat", page_icon="📈")

# first pass at a theme - way too much, scrapped it
# st.markdown(
#     """
#     <style>
#     .stApp { background-color: #1a0033; color: #39ff14; }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )

st.markdown(
    """
    <style>
    .stApp { background-color: #0b1e3d; color: #f2f2f2; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Portfolio & Articles Chatbot")
st.caption("Ask about anything you've saved below - articles or your holdings.")

if "store" not in st.session_state:
    st.session_state.store = RagStore()
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Add knowledge")

    with st.form("add_article_form", clear_on_submit=True):
        article_text = st.text_area("Paste an article")
        submitted_article = st.form_submit_button("Save article")
        if submitted_article and article_text.strip():
            st.session_state.store.add_document(article_text.strip(), source="article")
            st.success("Article saved")

    with st.form("add_portfolio_form", clear_on_submit=True):
        ticker = st.text_input("Ticker")
        shares = st.number_input("Shares", min_value=0.0, step=1.0)
        cost_basis = st.number_input("Cost basis ($/share)", min_value=0.0, step=0.01)
        note = st.text_input("Note (optional)")
        submitted_portfolio = st.form_submit_button("Save holding")
        if submitted_portfolio and ticker.strip():
            holding_text = (
                f"Portfolio holding: {shares} shares of {ticker.upper()} "
                f"at ${cost_basis:.2f} cost basis. {note}"
            ).strip()
            st.session_state.store.add_document(holding_text, source="portfolio")
            st.success("Holding saved")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

question = st.chat_input("Ask about your articles or portfolio...")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    context_docs = st.session_state.store.retrieve(question)
    answer = ask(question, context_docs)

    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.write(answer)
