"""Smoke tests for the AI Dev Portal backend."""



def test_import_council():
    """Test that the council module can be imported."""
    from ai.council import LLMCouncil

    assert LLMCouncil is not None


def test_import_llm_clients():
    """Test that LLM clients can be imported."""
    from ai.llm_clients import OpenRouterClient

    assert OpenRouterClient is not None


def test_import_config():
    """Test that config module can be imported."""
    from python.config import Settings

    assert Settings is not None
