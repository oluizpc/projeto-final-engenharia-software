"""
Testes de integracao dos endpoints (Aula 8), via TestClient.

A dependencia externa (Open Library) e mockada pela fixture `client`
em conftest.py — nenhum destes testes acessa a rede (Aula 9).
"""


def test_listar_livros_vazio(client):
    resposta = client.get("/livros")

    assert resposta.status_code == 200
    assert resposta.json() == []


def test_criar_e_listar_livro(client):
    resposta_criar = client.post(
        "/livros",
        json={"titulo": "Dom Casmurro", "autor": "Machado de Assis", "ano": 1899, "isbn": "111"},
    )
    assert resposta_criar.status_code == 201
    livro = resposta_criar.json()
    assert livro["id"] == 1
    assert livro["titulo"] == "Dom Casmurro"

    resposta_listar = client.get("/livros")
    assert resposta_listar.status_code == 200
    assert len(resposta_listar.json()) == 1


def test_buscar_livro_existente(client):
    criado = client.post(
        "/livros", json={"titulo": "1984", "autor": "George Orwell", "ano": 1949, "isbn": "222"}
    ).json()

    resposta = client.get(f"/livros/{criado['id']}")

    assert resposta.status_code == 200
    assert resposta.json()["titulo"] == "1984"


def test_buscar_livro_inexistente(client):
    resposta = client.get("/livros/999")

    assert resposta.status_code == 404


def test_criar_livro_isbn_duplicado(client):
    dados = {"titulo": "Livro A", "autor": "Autor A", "ano": 2000, "isbn": "333"}
    client.post("/livros", json=dados)

    resposta = client.post(
        "/livros", json={"titulo": "Livro B", "autor": "Autor B", "ano": 2010, "isbn": "333"}
    )

    assert resposta.status_code == 409


def test_criar_livro_completa_dados_via_open_library(client, cliente_externo_falso):
    cliente_externo_falso.dados = {"titulo": "Titulo da Open Library", "autor": "Autor da Open Library"}

    resposta = client.post("/livros", json={"ano": 2000, "isbn": "444"})

    assert resposta.status_code == 201
    livro = resposta.json()
    assert livro["titulo"] == "Titulo da Open Library"
    assert livro["autor"] == "Autor da Open Library"
    assert cliente_externo_falso.chamadas == ["444"]


def test_criar_livro_sem_dados_suficientes_retorna_422(client, cliente_externo_falso):
    cliente_externo_falso.dados = None

    resposta = client.post("/livros", json={"ano": 2000, "isbn": "555"})

    assert resposta.status_code == 422


def test_atualizar_livro_existente(client):
    criado = client.post(
        "/livros", json={"titulo": "Livro X", "autor": "Autor X", "ano": 2000, "isbn": "666"}
    ).json()

    resposta = client.put(
        f"/livros/{criado['id']}",
        json={"titulo": "Livro X Revisado", "autor": "Autor X", "ano": 2001, "isbn": "666"},
    )

    assert resposta.status_code == 200
    assert resposta.json()["titulo"] == "Livro X Revisado"


def test_atualizar_livro_inexistente(client):
    resposta = client.put(
        "/livros/999",
        json={"titulo": "X", "autor": "Y", "ano": 2000, "isbn": "1"},
    )

    assert resposta.status_code == 404


def test_remover_livro_existente(client):
    criado = client.post(
        "/livros", json={"titulo": "Livro Y", "autor": "Autor Y", "ano": 2000, "isbn": "777"}
    ).json()

    resposta = client.delete(f"/livros/{criado['id']}")

    assert resposta.status_code == 200
    assert client.get(f"/livros/{criado['id']}").status_code == 404


def test_remover_livro_inexistente(client):
    resposta = client.delete("/livros/999")

    assert resposta.status_code == 404
