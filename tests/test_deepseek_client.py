from unittest.mock import MagicMock, patch

import deepseek_client


def test_ask_sends_context_and_question_to_deepseek(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "fake-key")

    fake_response = MagicMock()
    fake_response.choices[0].message.content = "Apple's sales were strong."

    fake_client = MagicMock()
    fake_client.chat.completions.create.return_value = fake_response

    with patch("deepseek_client.OpenAI", return_value=fake_client):
        answer = deepseek_client.ask(
            "How were Apple's sales?",
            [{"text": "Apple reported record sales.", "source": "article"}],
        )

    assert answer == "Apple's sales were strong."
    sent_messages = fake_client.chat.completions.create.call_args.kwargs["messages"]
    assert "Apple reported record sales." in sent_messages[0]["content"]
    assert sent_messages[1]["content"] == "How were Apple's sales?"


def test_ask_handles_no_context(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "fake-key")

    fake_response = MagicMock()
    fake_response.choices[0].message.content = "I don't have notes on that."

    fake_client = MagicMock()
    fake_client.chat.completions.create.return_value = fake_response

    with patch("deepseek_client.OpenAI", return_value=fake_client):
        answer = deepseek_client.ask("Random question", [])

    assert answer == "I don't have notes on that."
