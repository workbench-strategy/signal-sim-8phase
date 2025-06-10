# tests/llm/test_wrapper.py
def test_openai():
    from src.llm.openai import call_openai
    assert "OpenAI response" in call_openai("test")
