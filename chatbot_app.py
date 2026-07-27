"""Capstone-style RAG chatbot - ask questions over your saved articles and
stock portfolio notes.

Run with:
    streamlit run chatbot_app.py
"""
from __future__ import annotations

import streamlit as st
from dotenv import load_dotenv

from deepseek_client import ask
from pdf_ingest import extract_pdf_text
from rag_store import RagStore
from ticker_lookup import company_name

load_dotenv()

st.set_page_config(page_title="Portfolio Chat", page_icon="📈")

# tried inline CSS on .stApp for the theme first, but it only colors the page
# background - chat message text has its own styles underneath and stayed low
# contrast. moved the theme into .streamlit/config.toml instead, which
# actually cascades into the chat bubbles/sidebar/buttons properly.

st.title("Portfolio & Articles Chatbot")
st.caption("Ask about anything you've saved below - articles or your holdings.")

if "store" not in st.session_state:
    st.session_state.store = RagStore()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_tokens" not in st.session_state:
    st.session_state.session_tokens = 0
if "session_cost" not in st.session_state:
    st.session_state.session_cost = 0.0
if "synced_embedding_tokens" not in st.session_state:
    st.session_state.synced_embedding_tokens = 0
if "synced_embedding_cost" not in st.session_state:
    st.session_state.synced_embedding_cost = 0.0


def _sync_embedding_usage() -> None:
    # store.embedding_tokens/cost are running totals for the store's whole
    # lifetime (including load-time backfills) - only add the new-since-last-
    # sync portion to the session counter, not the running total itself
    store = st.session_state.store
    st.session_state.session_tokens += store.embedding_tokens - st.session_state.synced_embedding_tokens
    st.session_state.session_cost += store.embedding_cost_usd - st.session_state.synced_embedding_cost
    st.session_state.synced_embedding_tokens = store.embedding_tokens
    st.session_state.synced_embedding_cost = store.embedding_cost_usd


_sync_embedding_usage()  # picks up any load-time backfill cost from RagStore._load

with st.sidebar:
    st.header("Add knowledge")

    with st.form("add_article_form", clear_on_submit=True):
        article_text = st.text_area("Paste an article")
        submitted_article = st.form_submit_button("Save article")
        if submitted_article and article_text.strip():
            st.session_state.store.add_document(article_text.strip(), source="article")
            _sync_embedding_usage()
            st.success("Article saved")

    pdf_file = st.file_uploader("...or upload a PDF article", type="pdf")
    if pdf_file is not None:
        pdf_text = extract_pdf_text(pdf_file)
        if pdf_text:
            st.session_state.store.add_document(pdf_text, source="article")
            _sync_embedding_usage()
            st.success(f"Extracted {len(pdf_text)} characters from {pdf_file.name}")
        else:
            st.warning("Couldn't pull any text out of that PDF - might be a scanned image.")

    with st.form("add_portfolio_form", clear_on_submit=True):
        ticker = st.text_input("Ticker")
        shares = st.number_input("Shares", min_value=0.0, step=1.0)
        cost_basis = st.number_input("Cost basis ($/share)", min_value=0.0, step=0.01)
        note = st.text_input("Note (optional)")
        submitted_portfolio = st.form_submit_button("Save holding")
        if submitted_portfolio and ticker.strip():
            symbol = ticker.upper()
            name = company_name(symbol)
            ticker_label = f"{symbol} ({name})" if name else symbol
            holding_text = (
                f"Portfolio holding: {shares} shares of {ticker_label} "
                f"at ${cost_basis:.2f} cost basis. {note}"
            ).strip()
            st.session_state.store.add_document(holding_text, source="portfolio", ticker=symbol)
            _sync_embedding_usage()
            st.success("Holding saved")

    st.divider()
    st.caption("Saved notes")
    if st.session_state.store.documents:
        for i, doc in enumerate(st.session_state.store.documents):
            label = doc["text"] if len(doc["text"]) <= 70 else doc["text"][:67] + "..."
            col1, col2 = st.columns([6, 1])
            col1.caption(f"[{doc['source']}] {label}")
            if col2.button("✕", key=f"delete_{i}", help="Remove this note"):
                st.session_state.store.remove_document(i)
                st.rerun()
    else:
        st.caption("Nothing saved yet.")

    st.divider()
    st.caption(
        f"Session usage: {st.session_state.session_tokens:,} tokens, "
        f"~${st.session_state.session_cost:.4f}"
    )

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message["role"] == "assistant":
            if message["sources"]:
                tags = ", ".join(f"{doc['source']} ({doc['score']:.2f})" for doc in message["sources"])
                st.caption(f"Sources: {tags}")
            else:
                st.caption("Not grounded - nothing in your saved notes matched this question.")

question = st.chat_input("Ask about your articles or portfolio...")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    context_docs = st.session_state.store.retrieve(question)
    _sync_embedding_usage()
    result = ask(question, context_docs)

    st.session_state.session_tokens += result.total_tokens
    st.session_state.session_cost += result.estimated_cost_usd

    st.session_state.messages.append(
        {"role": "assistant", "content": result.answer, "sources": context_docs}
    )
    with st.chat_message("assistant"):
        st.write(result.answer)
        if context_docs:
            tags = ", ".join(f"{doc['source']} ({doc['score']:.2f})" for doc in context_docs)
            st.caption(f"Sources: {tags}")
        else:
            st.caption("Not grounded - nothing in your saved notes matched this question.")
