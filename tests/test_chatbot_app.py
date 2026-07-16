from streamlit.testing.v1 import AppTest


def test_chatbot_app_loads_without_error():
    at = AppTest.from_file("chatbot_app.py").run()

    assert not at.exception
    assert at.title[0].value == "Portfolio & Articles Chatbot"


def test_sidebar_shows_add_knowledge_section():
    at = AppTest.from_file("chatbot_app.py").run()

    headers = [h.value for h in at.sidebar.header]
    assert "Add knowledge" in headers
