# Empresta 📚

Sistema de **biblioteca compartilhada**: cada usuário cadastra seus livros, empresta para outras pessoas, registra a devolução e avalia como foi o empréstimo.

![Tela inicial](docs/screenshot.png)

## Funcionalidades

- Cadastro e login de usuários com sessão
- Cadastro de livros com capa, autor, editora, número de páginas, categoria e nota
- Empréstimo e devolução de livros, com controle de disponibilidade
- Histórico de empréstimos por livro
- Avaliação do empréstimo (Péssimo, Ruim, Bom, Ótimo)
- Tela "Seus empréstimos" com os livros emprestados pelo usuário

## Stack

Python · Django (templates server-side) · SQLite · HTML/CSS

## Arquitetura

```
Empresta-/
├── biblioteca/   settings e rotas principais
├── usuarios/     cadastro, login e logout
├── livro/        livros, categorias, empréstimos e avaliações
├── index/        páginas institucionais (home e sobre)
└── templates/    layout base
```

### Modelo de dados

- **Usuario**: nome, e-mail e senha
- **Categoria**: agrupa os livros
- **Livros**: pertence a um Usuario e a uma Categoria, com flag `emprestado`
- **Emprestimo**: liga um Livro a quem pegou emprestado, com datas e avaliação

## Como rodar

**Pré-requisitos:** Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
echo "SECRET_KEY=troque-esta-chave" > .env
python manage.py migrate
python manage.py runserver
```

Acesse `http://localhost:8000/auth/cadastro/`.

## Testes

```bash
python manage.py test
```

## Autora

Feito por [Naiara Rodrigues](https://github.com/naiarar).
