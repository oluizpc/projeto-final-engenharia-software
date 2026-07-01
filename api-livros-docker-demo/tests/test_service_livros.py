"""Testes unitarios da regra de negocio em ServicoLivros (Aula 8)."""

from unittest.mock import MagicMock

import pytest

from exceptions import DadosLivroIncompletosError, IsbnDuplicadoError
from main import ServicoLivros
from models import Livro, LivroAtualizar, LivroCriar
from openlibrary_client import ClienteLivrosExternos
from repository import RepositorioLivros


def _repo_mock(livro_existente: Livro | None = None) -> MagicMock:
    repo = MagicMock(spec=RepositorioLivros)
    repo.buscar_por_isbn.return_value = livro_existente
    return repo


def _cliente_mock(retorno: dict | None = None) -> MagicMock:
    cliente = MagicMock(spec=ClienteLivrosExternos)
    cliente.buscar_por_isbn.return_value = retorno
    return cliente


def test_criar_recusa_isbn_duplicado():
    livro_existente = Livro(id=1, titulo="X", autor="Y", ano=2000, isbn="123")
    repo = _repo_mock(livro_existente=livro_existente)
    cliente = _cliente_mock()
    servico = ServicoLivros(repo, cliente)

    with pytest.raises(IsbnDuplicadoError):
        servico.criar(LivroCriar(titulo="Novo", autor="Autor", ano=2020, isbn="123"))

    repo.adicionar.assert_not_called()
    cliente.buscar_por_isbn.assert_not_called()


def test_criar_nao_consulta_open_library_quando_titulo_e_autor_informados():
    repo = _repo_mock()
    cliente = _cliente_mock()
    servico = ServicoLivros(repo, cliente)

    servico.criar(LivroCriar(titulo="Dom Casmurro", autor="Machado de Assis", ano=1899, isbn="111"))

    cliente.buscar_por_isbn.assert_not_called()
    repo.adicionar.assert_called_once()


def test_criar_completa_titulo_e_autor_via_open_library():
    repo = _repo_mock()
    cliente = _cliente_mock(retorno={"titulo": "Zen Speaks", "autor": "Zhizhong Cai"})
    servico = ServicoLivros(repo, cliente)

    servico.criar(LivroCriar(ano=2000, isbn="0385472579"))

    cliente.buscar_por_isbn.assert_called_once_with("0385472579")
    dados_enviados = repo.adicionar.call_args[0][0]
    assert dados_enviados.titulo == "Zen Speaks"
    assert dados_enviados.autor == "Zhizhong Cai"


def test_criar_completa_apenas_o_campo_faltante():
    repo = _repo_mock()
    cliente = _cliente_mock(
        retorno={"titulo": "Titulo da Open Library", "autor": "Autor da Open Library"}
    )
    servico = ServicoLivros(repo, cliente)

    servico.criar(LivroCriar(titulo="Titulo Informado", ano=2000, isbn="222"))

    dados_enviados = repo.adicionar.call_args[0][0]
    assert dados_enviados.titulo == "Titulo Informado"
    assert dados_enviados.autor == "Autor da Open Library"


def test_criar_levanta_erro_quando_dados_incompletos_e_open_library_nao_encontra():
    repo = _repo_mock()
    cliente = _cliente_mock(retorno=None)
    servico = ServicoLivros(repo, cliente)

    with pytest.raises(DadosLivroIncompletosError):
        servico.criar(LivroCriar(ano=2000, isbn="333"))

    repo.adicionar.assert_not_called()


def test_listar_delega_ao_repositorio():
    repo = _repo_mock()
    repo.listar.return_value = ["a", "b"]
    servico = ServicoLivros(repo, _cliente_mock())

    assert servico.listar() == ["a", "b"]


def test_buscar_delega_ao_repositorio():
    repo = _repo_mock()
    livro = Livro(id=1, titulo="X", autor="Y", ano=2000, isbn="1")
    repo.buscar_por_id.return_value = livro
    servico = ServicoLivros(repo, _cliente_mock())

    assert servico.buscar(1) is livro
    repo.buscar_por_id.assert_called_once_with(1)


def test_atualizar_delega_ao_repositorio():
    repo = _repo_mock()
    livro = Livro(id=1, titulo="X", autor="Y", ano=2000, isbn="1")
    repo.atualizar.return_value = livro
    servico = ServicoLivros(repo, _cliente_mock())

    dados = LivroAtualizar(titulo="X", autor="Y", ano=2000, isbn="1")
    assert servico.atualizar(1, dados) is livro
    repo.atualizar.assert_called_once_with(1, dados)


def test_remover_delega_ao_repositorio():
    repo = _repo_mock()
    repo.remover.return_value = True
    servico = ServicoLivros(repo, _cliente_mock())

    assert servico.remover(1) is True
    repo.remover.assert_called_once_with(1)
