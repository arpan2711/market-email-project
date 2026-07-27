from unittest.mock import MagicMock, patch

import embeddings_client


def make_fake_response(vectors, total_tokens=10):
    response = MagicMock()
    response.data = [MagicMock(embedding=vec) for vec in vectors]
    response.usage.total_tokens = total_tokens
    return response


def test_embed_normalizes_vectors(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fake-key")

    fake_client = MagicMock()
    fake_client.embeddings.create.return_value = make_fake_response([[3.0, 4.0]])

    with patch("embeddings_client.OpenAI", return_value=fake_client):
        result = embeddings_client.embed(["some text"])

    vec = result.vectors[0]
    assert abs(float((vec**2).sum()) ** 0.5 - 1.0) < 1e-6


def test_embed_tracks_tokens_and_cost(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fake-key")

    fake_client = MagicMock()
    fake_client.embeddings.create.return_value = make_fake_response(
        [[1.0, 0.0]], total_tokens=1_000_000
    )

    with patch("embeddings_client.OpenAI", return_value=fake_client):
        result = embeddings_client.embed(["some text"])

    assert result.total_tokens == 1_000_000
    assert result.estimated_cost_usd == embeddings_client.PRICE_PER_MILLION_TOKENS


def test_embed_sends_all_texts_in_one_call(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fake-key")

    fake_client = MagicMock()
    fake_client.embeddings.create.return_value = make_fake_response([[1.0, 0.0], [0.0, 1.0]])

    with patch("embeddings_client.OpenAI", return_value=fake_client):
        embeddings_client.embed(["first", "second"])

    sent_input = fake_client.embeddings.create.call_args.kwargs["input"]
    assert sent_input == ["first", "second"]
