from rag_store import RagStore


def test_add_and_retrieve_relevant_document(tmp_path):
    store = RagStore(path=tmp_path / "docs.json")
    store.add_document("Apple reported record iPhone sales this quarter.", source="article")
    store.add_document("Portfolio holding: 10 shares of TSLA at $200 cost basis.", source="portfolio")

    results = store.retrieve("How did Apple's iPhone sales do?")

    assert results
    assert results[0]["source"] == "article"


def test_retrieve_on_empty_store_returns_empty_list(tmp_path):
    store = RagStore(path=tmp_path / "docs.json")
    assert store.retrieve("anything") == []


def test_documents_persist_across_instances(tmp_path):
    path = tmp_path / "docs.json"
    store = RagStore(path=path)
    store.add_document("Some article text", source="article")

    reloaded = RagStore(path=path)
    assert len(reloaded.documents) == 1
    assert reloaded.documents[0]["text"] == "Some article text"
