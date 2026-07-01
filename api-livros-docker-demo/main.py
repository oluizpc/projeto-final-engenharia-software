"""
API REST de catalogo de livros (FastAPI).

Estrutura em camadas:
  - Rotas (este arquivo): recebem a requisicao, chamam o service, devolvem a resposta
  - Service: regras de negocio
  - Repository (repository.py): guarda e recupera os dados

Para rodar:
  pip install fastapi uvicorn
  uvicorn main:app --reload

Documentacao interativa: http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException, status

from exceptions import DadosLivroIncompletosError, IsbnDuplicadoError
from models import Livro, LivroCriar, LivroAtualizar
from openlibrary_client import ClienteLivrosExternos, OpenLibraryClient
from repository import RepositorioEmMemoria, RepositorioLivros


# ----------------------------------------------------------------------
# Camada de servico (regras de negocio)
# ----------------------------------------------------------------------

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


# ----------------------------------------------------------------------
# Montagem da aplicacao
# ----------------------------------------------------------------------

app = FastAPI(title="Catalogo de Livros", version="1.0.0")

# Injecao de dependencia simples: trocar as linhas abaixo por outras
# implementacoes de RepositorioLivros/ClienteLivrosExternos nao exige
# mudar mais nada (e e exatamente o que os testes fazem com mocks).
servico = ServicoLivros(RepositorioEmMemoria(), OpenLibraryClient())


# ----------------------------------------------------------------------
# Rotas (camada de API)
# ----------------------------------------------------------------------

@app.get("/livros", response_model=list[Livro])
def listar_livros():
    return servico.listar()


@app.get("/livros/{livro_id}", response_model=Livro)
def buscar_livro(livro_id: int):
    livro = servico.buscar(livro_id)
    if livro is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Livro nao encontrado",
        )
    return livro


@app.post("/livros", response_model=Livro, status_code=status.HTTP_201_CREATED)
def criar_livro(dados: LivroCriar):
    try:
        return servico.criar(dados)
    except IsbnDuplicadoError as erro:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(erro)
        ) from erro
    except DadosLivroIncompletosError as erro:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(erro)
        ) from erro


@app.put("/livros/{livro_id}", response_model=Livro)
def atualizar_livro(livro_id: int, dados: LivroAtualizar):
    livro = servico.atualizar(livro_id, dados)
    if livro is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Livro nao encontrado",
        )
    return livro


@app.delete("/livros/{livro_id}", status_code=status.HTTP_200_OK)
def remover_livro(livro_id: int):
    removido = servico.remover(livro_id)
    if not removido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Livro nao encontrado",
        )
    return {"mensagem": "Livro removido com sucesso"}
