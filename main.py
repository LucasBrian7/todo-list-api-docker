
import os
import secrets
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from sqlalchemy import String, Text, Boolean, Integer, select, func
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./tarefas.db",
)

USUARIO_CORRETO = os.getenv("API_USERNAME", "lucas")
SENHA_CORRETA = os.getenv("API_PASSWORD", "123456")

engine = create_async_engine(DATABASE_URL)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


class TarefaDB(Base):
    __tablename__ = "tarefas"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    nome: Mapped[str] = mapped_column(
        String(100),
        index=True,
    )

    descricao: Mapped[str] = mapped_column(Text)

    concluida: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )


class Tarefa(BaseModel):
    nome: str
    descricao: str
    concluida: bool = False


security = HTTPBasic()


def autenticar(
    credenciais: HTTPBasicCredentials = Depends(security),
):
    usuario_valido = secrets.compare_digest(
        credenciais.username.encode("utf-8"),
        USUARIO_CORRETO.encode("utf-8"),
    )

    senha_valida = secrets.compare_digest(
        credenciais.password.encode("utf-8"),
        SENHA_CORRETA.encode("utf-8"),
    )

    if not (usuario_valido and senha_valida):
        raise HTTPException(
            status_code=401,
            detail="Usuario ou senha incorretos!",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credenciais.username


async def obter_sessao():
    async with SessionLocal() as sessao:
        yield sessao


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conexao:
        await conexao.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.get("/tarefas")
async def get_tarefas(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    order_by: str = Query(default="nome"),
    usuario: str = Depends(autenticar),
    sessao: AsyncSession = Depends(obter_sessao),
):
    campos_validos = ["nome", "descricao", "concluida"]

    if order_by not in campos_validos:
        raise HTTPException(
            status_code=400,
            detail=(
                "Campo de ordenacao invalido. "
                "Use: nome, descricao ou concluida."
            ),
        )

    resultado_total = await sessao.execute(
        select(func.count()).select_from(TarefaDB)
    )

    total = resultado_total.scalar_one()

    campo_ordenacao = getattr(TarefaDB, order_by)

    consulta = (
        select(TarefaDB)
        .order_by(campo_ordenacao)
        .offset((page - 1) * size)
        .limit(size)
    )

    resultado = await sessao.execute(consulta)
    tarefas_paginadas = resultado.scalars().all()

    return {
        "page": page,
        "size": size,
        "total": total,
        "total_paginas": (total + size - 1) // size,
        "order_by": order_by,
        "tarefas": [
            {
                "nome": tarefa.nome,
                "descricao": tarefa.descricao,
                "concluida": tarefa.concluida,
            }
            for tarefa in tarefas_paginadas
        ],
    }


@app.post("/tarefas")
async def post_tarefa(
    tarefa: Tarefa,
    usuario: str = Depends(autenticar),
    sessao: AsyncSession = Depends(obter_sessao),
):
    nova_tarefa = TarefaDB(
        nome=tarefa.nome,
        descricao=tarefa.descricao,
        concluida=tarefa.concluida,
    )

    sessao.add(nova_tarefa)

    await sessao.commit()
    await sessao.refresh(nova_tarefa)

    return {
        "message": "A tarefa foi criada com sucesso!",
        "tarefa": {
            "nome": nova_tarefa.nome,
            "descricao": nova_tarefa.descricao,
            "concluida": nova_tarefa.concluida,
        },
    }


@app.put("/tarefas/{nome}")
async def concluir_tarefa(
    nome: str,
    usuario: str = Depends(autenticar),
    sessao: AsyncSession = Depends(obter_sessao),
):
    resultado = await sessao.execute(
        select(TarefaDB).where(TarefaDB.nome == nome)
    )

    tarefa = resultado.scalars().first()

    if tarefa is None:
        raise HTTPException(
            status_code=404,
            detail="Tarefa nao encontrada!",
        )

    tarefa.concluida = True

    await sessao.commit()
    await sessao.refresh(tarefa)

    return {
        "message": "A tarefa foi concluida com sucesso!",
        "tarefa": {
            "nome": tarefa.nome,
            "descricao": tarefa.descricao,
            "concluida": tarefa.concluida,
        },
    }


@app.delete("/tarefas/{nome}")
async def deletar_tarefa(
    nome: str,
    usuario: str = Depends(autenticar),
    sessao: AsyncSession = Depends(obter_sessao),
):
    resultado = await sessao.execute(
        select(TarefaDB).where(TarefaDB.nome == nome)
    )

    tarefa = resultado.scalars().first()

    if tarefa is None:
        raise HTTPException(
            status_code=404,
            detail="Tarefa nao encontrada!",
        )

    await sessao.delete(tarefa)
    await sessao.commit()

    return {
        "message": "A tarefa foi removida com sucesso!"
    }
