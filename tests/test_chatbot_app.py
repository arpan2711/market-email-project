from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from conftest import fake_embed

# the local data/rag_documents.json may have notes saved before the
# embeddings upgrade, which RagStore backfills on load - patch the embedding
# call so that backfill (and the app loading in general) doesn't need a real
# OPENAI_API_KEY or network access just to run this smoke test
patched_embed = patch("rag_store.embed", side_effect=fake_embed)


def test_chatbot_app_loads_without_error():
    with patched_embed:
        at = AppTest.from_file("chatbot_app.py").run()

    assert not at.exception
    assert at.title[0].value == "Portfolio & Articles Chatbot"


def test_sidebar_shows_add_knowledge_section():
    with patched_embed:
        at = AppTest.from_file("chatbot_app.py").run()

    headers = [h.value for h in at.sidebar.header]
    assert "Add knowledge" in headers
