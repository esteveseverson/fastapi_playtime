# Playtime
## Visão Geral
O projeto FastAPI Playtime é uma aplicação web desenvolvida com o framework FastAPI, que tem como objetivo gerenciar agendamentos de quadras de esportes. O sistema oferece recursos para autenticação de usuários, criação e visualização de agendamentos, além de permitir a criação e manipulação de quadras.

## Tecnologias Utilizadas:
- FastAPI: Framework para construção da API, conhecido por sua performance e validação automática de dados.
- SQLAlchemy: ORM (Object-Relational Mapping) utilizado para interação com o banco de dados.
- Alembic: Ferramenta para gerenciamento de migrações do banco de dados.
- JWT (JSON Web Tokens): Método utilizado para autenticação dos usuários via token.
- Pydantic: Biblioteca para validação de dados e parsing de informações.
- Poetry: Ferramenta de gerenciamento de dependências e pacotes do Python.
---

## Estrutura do Projeto
```
fastapi_playtime/
├─ fastapi_playtime/
│  ├─ models/                 # Contém os modelos de dados (agendamento, quadra, usuário, etc.)
│  │  ├─ agendamento.py
│  │  ├─ quadra.py
│  │  ├─ user.py
│  ├─ routers/                # Contém as rotas da API
│  │  ├─ agendamento.py
│  │  ├─ agendamentos_nomeados.py
│  │  ├─ auth.py
│  │  ├─ current_user.py
│  │  ├─ horarios_disponiveis.py
│  │  ├─ quadra.py
│  │  ├─ users.py
│  ├─ schemas/                # Contém os schemas Pydantic para validação de dados
│  │  ├─ agendamento.py
│  │  ├─ auth.py
│  │  ├─ comum.py
│  │  ├─ horarios_disponiveis.py
│  │  ├─ quadra.py
│  │  ├─ user.py
│  ├─ utils/                  # Utilitários do projeto
│  │  ├─ datetime_format.py
│  │  ├─ test.py
│  ├─ app.py                  # Arquivo principal para iniciar o servidor
│  ├─ database.py             # Configuração do banco de dados
│  ├─ security.py             # Configuração de segurança (JWT)
│  ├─ settings.py             # Configurações do projeto (como variáveis de ambiente)
│  ├─ __init__.py
tests/
.gitignore                    # Arquivo de configuração para ignorar arquivos sensíveis
doc.md                        # Documentação das rotas da API
poetry.lock                   # Arquivo de bloqueio do Poetry
pyproject.toml                # Arquivo de configuração do ambiente
README.md                     # Documento com a visão geral do projeto
```
---

## Instalação
1. Clone o repositório: <br>
` git clone https://github.com/esteveseverson/fastapi_playtime `
2. Acesse o diretório:
` cd fastapi_playtime `
3. Instale as dependências:
` poetry install `
4. Crie um arquivo .env com as seguintes variaveis:
```.env
DATABASE_URL="" -> para rodar localmente com o SQLite use "sqlite:///database.db"
SECRET_KEY="" -> pode ser qualquer uma
ALGORITHM="" -> HS256
ACCESS_TOKEN_EXPIRE_MINUTES="" -> tempo em minutos para o token jwt expirar
```
5. Execute o código:
` poetry run task run ` naturalmente a API iniciará em 127.0.0.1, para ver o swagger vá para 127.0.0.1/docs
---

## Como utilizar a API <br>
- A documentação das rotas está no arquivo [doc.md](https://github.com/esteveseverson/fastapi_playtime/blob/master/doc.md). <br>
- A maioria das rotas necessita de autenticação, então após criar um usuário use a autenticação do swagger no canto superior direito. <br>
---
