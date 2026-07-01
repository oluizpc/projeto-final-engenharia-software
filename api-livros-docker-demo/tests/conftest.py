"""Fixtures compartilhadas pelos testes de integracao da API."""

import pytest
from fastapi.testclient import TestClient

import main
from openlibrary_client import ClienteLivrosExternos
from repository import RepositorioEmMemoria


class ClienteExternoFalso(ClienteLivrosExternos):
    """
    Dublê de teste para a Open Library: nunca acessa a rede, apenas
    devolve os dados configurados pelo teste (Aula 9 - mock da
    dependência externa).
    """

    def __init__(self) -> None:
        self.dados: dict | None = None
        self.chamadas: list[str] = []

    def buscar_por_isbn(self, isbn: str) -> dict | None:
        self.chamadas.append(isbn)
        return self.dados


@pytest.fixture
def cliente_externo_falso() -> ClienteExternoFalso:
    return ClienteExternoFalso()


@pytest.fixture
def client(monkeypatch, cliente_externo_falso) -> TestClient:
    """TestClient com repositorio limpo a cada teste e Open Library mockada."""
    monkeypatch.setattr(
        main, "servico", main.ServicoLivros(RepositorioEmMemoria(), cliente_externo_falso)
    )
    return TestClient(main.app)
