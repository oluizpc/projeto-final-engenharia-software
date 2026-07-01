"""Testes do RepositorioEmMemoria."""

from models import LivroAtualizar, LivroCriar
from repository import RepositorioEmMemoria


def _dados(isbn: str = "123") -> LivroCriar:
    return LivroCriar(titulo="Titulo", autor="Autor", ano=2000, isbn=isbn)


def test_adicionar_gera_id_incremental():
    repo = RepositorioEmMemoria()
    primeiro = repo.adicionar(_dados("1"))
    segundo = repo.adicionar(_dados("2"))

    assert primeiro.id == 1
    assert segundo.id == 2


def test_buscar_por_id_inexistente_retorna_none():
    repo = RepositorioEmMemoria()
    assert repo.buscar_por_id(999) is None


def test_buscar_por_isbn_encontra_e_nao_encontra():
    repo = RepositorioEmMemoria()
    livro = repo.adicionar(_dados("789"))

    assert repo.buscar_por_isbn("789") == livro
    assert repo.buscar_por_isbn("000") is None


def test_atualizar_inexistente_retorna_none():
    repo = RepositorioEmMemoria()
    dados = LivroAtualizar(titulo="X", autor="Y", ano=2000, isbn="1")

    assert repo.atualizar(999, dados) is None


def test_atualizar_existente():
    repo = RepositorioEmMemoria()
    livro = repo.adicionar(_dados("1"))
    dados = LivroAtualizar(titulo="Novo Titulo", autor="Novo Autor", ano=2021, isbn="1")

    atualizado = repo.atualizar(livro.id, dados)

    assert atualizado.titulo == "Novo Titulo"
    assert repo.buscar_por_id(livro.id).titulo == "Novo Titulo"


def test_remover_inexistente_retorna_false():
    repo = RepositorioEmMemoria()
    assert repo.remover(999) is False


def test_remover_existente():
    repo = RepositorioEmMemoria()
    livro = repo.adicionar(_dados("1"))

    assert repo.remover(livro.id) is True
    assert repo.buscar_por_id(livro.id) is None
