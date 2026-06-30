"""
Testes do OpenLibraryClient.

Toda chamada de rede e mockada (Aula 9): httpx.get e substituido, entao
estes testes nao dependem da internet nem da disponibilidade da Open
Library.
"""

from unittest.mock import MagicMock, patch

import httpx

from openlibrary_client import OpenLibraryClient


def _resposta_falsa(json_data: dict) -> MagicMock:
    resposta = MagicMock()
    resposta.json.return_value = json_data
    resposta.raise_for_status = MagicMock()
    return resposta


@patch("openlibrary_client.httpx.get")
def test_buscar_por_isbn_encontrado(mock_get):
    mock_get.return_value = _resposta_falsa(
        {
            "ISBN:0385472579": {
                "title": "Zen Speaks",
                "authors": [{"name": "Zhizhong Cai", "url": "https://openlibrary.org/x"}],
            }
        }
    )

    resultado = OpenLibraryClient().buscar_por_isbn("0385472579")

    assert resultado == {"titulo": "Zen Speaks", "autor": "Zhizhong Cai"}
    mock_get.assert_called_once()


@patch("openlibrary_client.httpx.get")
def test_buscar_por_isbn_nao_encontrado(mock_get):
    mock_get.return_value = _resposta_falsa({})

    resultado = OpenLibraryClient().buscar_por_isbn("0000000000")

    assert resultado is None


@patch("openlibrary_client.httpx.get")
def test_buscar_por_isbn_sem_autores_listados(mock_get):
    mock_get.return_value = _resposta_falsa({"ISBN:123": {"title": "Sem autor listado"}})

    resultado = OpenLibraryClient().buscar_por_isbn("123")

    assert resultado == {"titulo": "Sem autor listado", "autor": None}


@patch("openlibrary_client.httpx.get")
def test_buscar_por_isbn_erro_de_rede_retorna_none(mock_get):
    mock_get.side_effect = httpx.ConnectError("falha simulada de rede")

    resultado = OpenLibraryClient().buscar_por_isbn("123")

    assert resultado is None


@patch("openlibrary_client.httpx.get")
def test_buscar_por_isbn_resposta_http_de_erro_retorna_none(mock_get):
    resposta = _resposta_falsa({})
    resposta.raise_for_status.side_effect = httpx.HTTPStatusError(
        "erro", request=MagicMock(), response=MagicMock()
    )
    mock_get.return_value = resposta

    resultado = OpenLibraryClient().buscar_por_isbn("123")

    assert resultado is None
