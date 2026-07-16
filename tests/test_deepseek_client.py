from unittest.mock import MagicMock, patch

import deepseek_client


def make_fake_response(content, prompt_tokens=100, completion_tokens=50):
    response = MagicMock()
    response.choices[0].message.content = content
    response.usage.prompt_tokens = prompt_tokens
    response.usage.completion_tokens = completion_tokens
    response.usage.total_tokens = prompt_tokens + completion_tokens
    return response


def test_ask_sends_context_and_question_to_deepseek(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "fake-key")

    fake_client = MagicMock()
    fake_client.chat.completions.create.return_value = make_fake_response("Apple's sales were strong.")

    with patch("deepseek_client.OpenAI", return_value=fake_client):
        result = deepseek_client.ask(
            "How were Apple's sales?",
            [{"text": "Apple reported record sales.", "source": "article"}],
        )

    assert result.answer == "Apple's sales were strong."
    sent_messages = fake_client.chat.completions.create.call_args.kwargs["messages"]
    assert "Apple reported record sales." in sent_messages[0]["content"]
    assert sent_messages[1]["content"] == "How were Apple's sales?"


def test_ask_handles_no_context(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "fake-key")

    fake_client = MagicMock()
    fake_client.chat.completions.create.return_value = make_fake_response("I don't have notes on that.")

    with patch("deepseek_client.OpenAI", return_value=fake_client):
        result = deepseek_client.ask("Random question", [])

    assert result.answer == "I don't have notes on that."


def test_ask_tracks_token_usage_and_cost(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "fake-key")

    fake_client = MagicMock()
    fake_client.chat.completions.create.return_value = make_fake_response(
        "answer", prompt_tokens=1_000_000, completion_tokens=1_000_000
    )

    with patch("deepseek_client.OpenAI", return_value=fake_client):
        result = deepseek_client.ask("q", [])

    assert result.prompt_tokens == 1_000_000
    assert result.completion_tokens == 1_000_000
    assert result.total_tokens == 2_000_000

    expected_cost = (
        deepseek_client.PRICE_PER_MILLION_INPUT_TOKENS
        + deepseek_client.PRICE_PER_MILLION_OUTPUT_TOKENS
    )
    assert result.estimated_cost_usd == expected_cost
