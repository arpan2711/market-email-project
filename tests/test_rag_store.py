from unittest.mock import patch

from conftest import fake_embed
from rag_store import RagStore


def patched_embed():
    return patch("rag_store.embed", side_effect=fake_embed)


def test_add_and_retrieve_relevant_document(tmp_path):
    with patched_embed():
        store = RagStore(path=tmp_path / "docs.json")
        store.add_document("Apple reported record iPhone sales this quarter.", source="article")
        store.add_document("Portfolio holding: 10 shares of TSLA at $200 cost basis.", source="portfolio")

        results = store.retrieve("How did Apple's iPhone sales do?")

    assert results
    assert results[0]["source"] == "article"


def test_retrieve_includes_similarity_score(tmp_path):
    with patched_embed():
        store = RagStore(path=tmp_path / "docs.json")
        store.add_document("Apple reported record iPhone sales this quarter.", source="article")

        results = store.retrieve("Apple iPhone sales")

    assert "score" in results[0]
    assert 0 < results[0]["score"] <= 1


def test_retrieve_does_not_leak_the_raw_embedding(tmp_path):
    with patched_embed():
        store = RagStore(path=tmp_path / "docs.json")
        store.add_document("Apple reported record iPhone sales this quarter.", source="article")

        results = store.retrieve("Apple iPhone sales")

    assert "embedding" not in results[0]


def test_retrieve_on_empty_store_returns_empty_list(tmp_path):
    with patched_embed():
        assert RagStore(path=tmp_path / "docs.json").retrieve("anything") == []


def test_documents_persist_across_instances(tmp_path):
    path = tmp_path / "docs.json"
    with patched_embed():
        store = RagStore(path=path)
        store.add_document("Some article text", source="article")

        reloaded = RagStore(path=path)

    assert len(reloaded.documents) == 1
    assert reloaded.documents[0]["text"] == "Some article text"


def test_re_adding_a_ticker_replaces_the_old_holding(tmp_path):
    with patched_embed():
        store = RagStore(path=tmp_path / "docs.json")
        store.add_document("Portfolio holding: 10 shares of TSLA", source="portfolio", ticker="TSLA")
        store.add_document("Portfolio holding: 25 shares of TSLA", source="portfolio", ticker="TSLA")

    portfolio_docs = [doc for doc in store.documents if doc["source"] == "portfolio"]
    assert len(portfolio_docs) == 1
    assert portfolio_docs[0]["text"] == "Portfolio holding: 25 shares of TSLA"


def test_remove_document(tmp_path):
    path = tmp_path / "docs.json"
    with patched_embed():
        store = RagStore(path=path)
        store.add_document("Keep me", source="article")
        store.add_document("Delete me", source="article")

        store.remove_document(1)

        assert len(store.documents) == 1
        assert store.documents[0]["text"] == "Keep me"

        reloaded = RagStore(path=path)
    assert len(reloaded.documents) == 1


def test_load_backfills_embeddings_for_older_saved_documents(tmp_path):
    path = tmp_path / "docs.json"
    path.write_text('[{"text": "Old note saved before embeddings existed", "source": "article"}]')

    with patched_embed():
        store = RagStore(path=path)

    assert "embedding" in store.documents[0]
    assert store.embedding_tokens > 0
