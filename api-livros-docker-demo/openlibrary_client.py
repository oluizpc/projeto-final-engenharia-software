"""
Cliente da dependencia externa usada na extensao da API: a Open Library.

O service usa essa consulta para completar titulo/autor a partir do ISBN
quando o cliente da API nao os informa. Fica isolada atras da interface
ClienteLivrosExternos para que os testes possam substituir a chamada de
rede real por um mock (Aula 9) em vez de depender da internet.
"""

from abc import ABC, abstractmethod

import httpx

OPENLIBRARY_URL = "https://openlibrary.org/api/books"


class ClienteLivrosExternos(ABC):
    """Interface para consulta de dados de livros em uma fonte externa."""

    @abstractmethod
    def buscar_por_isbn(self, isbn: str) -> dict | None:
        """Retorna {"titulo": ..., "autor": ...} ou None se nao encontrado."""


class OpenLibraryClient(ClienteLivrosExternos):
    """Implementacao que consulta a API publica da Open Library."""

    def __init__(self, timeout: float = 5.0) -> None:
        self._timeout = timeout

    def buscar_por_isbn(self, isbn: str) -> dict | None:
        chave = f"ISBN:{isbn}"
        try:
            resposta = httpx.get(
                OPENLIBRARY_URL,
                params={"bibkeys": chave, "format": "json", "jscmd": "data"},
                timeout=self._timeout,
            )
            resposta.raise_for_status()
        except httpx.HTTPError:
            return None

        dados = resposta.json().get(chave)
        if not dados:
            return None

        autores = dados.get("authors") or []
        return {
            "titulo": dados.get("title"),
            "autor": autores[0]["name"] if autores else None,
        }
