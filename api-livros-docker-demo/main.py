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
from openlibrary_client import OpenLibraryClient
from repository import RepositorioEmMemoria
from service import ServicoLivros


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
