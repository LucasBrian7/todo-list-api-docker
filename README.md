
# API de Tarefas

API REST desenvolvida com Python, FastAPI, SQLAlchemy assíncrono e SQLite, utilizando Docker, Docker Compose e Poetry.

## Tecnologias

- Python 3.12
- FastAPI
- SQLAlchemy
- SQLite
- aiosqlite
- Poetry
- Docker
- Docker Compose

## Funcionalidades

- Criar tarefas
- Listar tarefas com paginação
- Ordenar tarefas por nome, descrição ou status
- Marcar tarefas como concluídas
- Excluir tarefas
- Autenticação HTTP Basic
- Persistência dos dados com SQLite

## Pré-requisitos

- Git
- Docker Desktop
- Docker Compose

No Windows, instale o Docker Desktop e aguarde até que o Docker esteja em execução.

## Como executar

### 1. Clonar o repositório

```bash
git clone URL_DO_SEU_REPOSITORIO
cd Todo_list
```

Substitua `URL_DO_SEU_REPOSITORIO` pelo endereço real do repositório no GitHub.

### 2. Configurar as variáveis de ambiente

Copie o arquivo de exemplo:

No PowerShell:

```powershell
Copy-Item .env.example .env
```

Edite o arquivo `.env` e defina suas credenciais.

### 3. Construir e iniciar a aplicação

```bash
docker compose up --build -d
```

O comando constrói a imagem, cria o container e inicia a API em segundo plano.

### 4. Verificar os logs

```bash
docker compose logs -f api
```

Para sair da visualização dos logs, pressione Ctrl+C. Isso não encerra o container.

### 5. Acessar a API

Documentação interativa:

http://localhost:8000/docs

Verificação da documentação OpenAPI:

http://localhost:8000/openapi.json

Utilize a autenticação HTTP Basic com as credenciais definidas no arquivo `.env`.

### 6. Parar a aplicação

```bash
docker compose down
```

Os dados do banco são preservados no volume Docker.

Para iniciar novamente:

```bash
docker compose up -d
```

### 7. Reconstruir a imagem

Se você alterar o Dockerfile ou as dependências:

```bash
docker compose up --build -d
```

### 8. Remover também os dados do banco

**Atenção:** este comando apaga o volume do banco de dados do projeto.

```bash
docker compose down -v
```

## Endpoints

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/tarefas` | Lista tarefas com paginação e ordenação |
| POST | `/tarefas` | Cria uma tarefa |
| PUT | `/tarefas/{nome}` | Marca uma tarefa como concluída |
| DELETE | `/tarefas/{nome}` | Exclui uma tarefa |

Todos os endpoints exigem autenticação HTTP Basic.

### Exemplo de criação de tarefa

Requisição `POST /tarefas`:

```json
{
  "nome": "Estudar Docker",
  "descricao": "Aprender Docker e Docker Compose",
  "concluida": false
}
```

### Exemplo de listagem

```text
GET /tarefas?page=1&size=10&order_by=nome
```

## Desenvolvimento

O código local é sincronizado com o container. O Uvicorn está configurado com `--reload` para recarregar a aplicação quando os arquivos Python forem alterados.

## Banco de dados

O SQLite é armazenado em um volume Docker nomeado, garantindo persistência entre reinicializações e recriações do container.

