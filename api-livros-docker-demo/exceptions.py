"""Excecoes de regra de negocio levantadas pela camada de service."""


class IsbnDuplicadoError(Exception):
    """Levantada ao tentar cadastrar um livro com ISBN ja existente."""

    def __init__(self, isbn: str) -> None:
        self.isbn = isbn
        super().__init__(f"Ja existe um livro cadastrado com o ISBN '{isbn}'")


class DadosLivroIncompletosError(Exception):
    """
    Levantada quando titulo/autor nao foram informados pelo cliente e
    tambem nao foram encontrados na Open Library para o ISBN informado.
    """

    def __init__(self, isbn: str) -> None:
        self.isbn = isbn
        super().__init__(
            f"Titulo e autor nao foram informados e nao foram encontrados "
            f"na Open Library para o ISBN '{isbn}'"
        )
