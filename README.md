# projeto-final-es

## Configuração do repositório (AWS)

Em Settings → Secrets and Variables → Actions → New repository secret, adicione:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_SESSION_TOKEN`

## Como rodar o projeto

### Local
1. `cd api-livros-docker-demo`
2. `pip install -r requirements-dev.txt`
3. `uvicorn main:app --reload`
4. Acesse a documentação em http://localhost:8000/docs

### Testes
\`\`\`
pytest --cov=. --cov-report=term-missing
\`\`\`

### Docker
\`\`\`
docker build -t api-livros .
docker run -p 8000:8000 api-livros
\`\`\`

## Endpoints principais
- `GET /livros` — lista todos os livros
- `POST /livros` — cria um livro (valida ISBN duplicado e busca dados na Open Library se título/autor não informados)
- `GET /livros/{id}` — busca por id
- `PUT /livros/{id}` — atualiza um livro
- `DELETE /livros/{id}` — remove um livro