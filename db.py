from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from sqlalchemy import text
from sqlmodel import Session, SQLModel, create_engine, select

from models import Comentario, Publicacion, Usuario

BASE_DIR = Path(__file__).resolve().parent
sqlite_name = BASE_DIR / "database.db"
sqlite_url = f"sqlite:///{sqlite_name}"

engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})


def ensure_publicacion_columns():
    with Session(engine) as session:
        columnas = [row[1] for row in session.exec(text("PRAGMA table_info(publicacion)")).all()]

        if "archivo_url" not in columnas:
            session.exec(text("ALTER TABLE publicacion ADD COLUMN archivo_url TEXT"))

        if "archivo_nombre" not in columnas:
            session.exec(text("ALTER TABLE publicacion ADD COLUMN archivo_nombre TEXT"))

        session.commit()


def remove_demo_accounts():
    demo_users = ["ana01", "juan_dev", "maria_art"]

    with Session(engine) as session:
        usuarios = session.exec(select(Usuario).where(Usuario.usuario.in_(demo_users))).all()
        if not usuarios:
            return

        usuario_ids = [usuario.id for usuario in usuarios if usuario.id is not None]
        if not usuario_ids:
            return

        publicaciones = session.exec(select(Publicacion).where(Publicacion.usuario_id.in_(usuario_ids))).all()
        publicacion_ids = [publicacion.id for publicacion in publicaciones if publicacion.id is not None]

        if publicacion_ids:
            comentarios = session.exec(select(Comentario).where(Comentario.publicacion_id.in_(publicacion_ids))).all()
            for comentario in comentarios:
                session.delete(comentario)

        for publicacion in publicaciones:
            session.delete(publicacion)

        for usuario in usuarios:
            session.delete(usuario)

        session.commit()


@asynccontextmanager
async def create_all_table(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    ensure_publicacion_columns()
    remove_demo_accounts()
    yield


def get_session():
    with Session(engine) as session:
        yield session
