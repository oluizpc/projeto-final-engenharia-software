"""
Camada de servico (regras de negocio) da API de catalogo de livros.

Fica separada das rotas (main.py) para que a logica de negocio possa ser
testada isoladamente, sem subir a aplicacao FastAPI (Aula 8).
"""

from exceptions import DadosLivroIncompletosError, IsbnDuplicadoError
from models import Livro, LivroAtualizar, LivroCriar
from openlibrary_client import ClienteLivrosExternos
from repository import RepositorioLivros


class ServicoLivros:
    """
    Onde mora a logica de negocio. Recebe um RepositorioLivros e um
    ClienteLivrosExternos pela interface --- nao sabe se o repositorio e
    em memoria/SQLite, nem se o cliente externo e a Open Library de
    verdade ou um mock de teste.
    """

    def __init__(
        self,
        repositorio: RepositorioLivros,
        cliente_externo: ClienteLivrosExternos,
    ) -> None:
        self._repo = repositorio
        self._cliente_externo = cliente_externo

    def listar(self) -> list[Livro]:
        return self._repo.listar()

    def buscar(self, livro_id: int) -> Livro | None:
        return self._repo.buscar_por_id(livro_id)

    def criar(self, dados: LivroCriar) -> Livro:
        if self._repo.buscar_por_isbn(dados.isbn) is not None:
            raise IsbnDuplicadoError(dados.isbn)

        titulo = dados.titulo
        autor = dados.autor
        if not titulo or not autor:
            encontrado = self._cliente_externo.buscar_por_isbn(dados.isbn)
            if encontrado:
                titulo = titulo or encontrado.get("titulo")
                autor = autor or encontrado.get("autor")

        if not titulo or not autor:
            raise DadosLivroIncompletosError(dados.isbn)

        dados_completos = LivroCriar(
            titulo=titulo, autor=autor, ano=dados.ano, isbn=dados.isbn
        )
        return self._repo.adicionar(dados_completos)

    def atualizar(self, livro_id: int, dados: LivroAtualizar) -> Livro | None:
        return self._repo.atualizar(livro_id, dados)

    def remover(self, livro_id: int) -> bool:
        return self._repo.remover(livro_id)
