"""Fixtures compartilhadas pelos testes."""

import pytest

from backend.app import criar_app


@pytest.fixture
def cliente_api():
    """Cliente de testes do Flask (não abre portas nem servidor)."""
    app = criar_app()
    app.config.update(TESTING=True)
    with app.test_client() as cliente:
        yield cliente
