from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from sqlmodel import Session, SQLModel, create_engine, select

from models import Comentario, Publicacion, Usuario

BASE_DIR = Path(__file__).resolve().parent
sqlite_name = BASE_DIR / "database.db"
sqlite_url = f"sqlite:///{sqlite_name}"

engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})


def seed_data():
    """Carga datos de ejemplo solo si la base está vacía."""
    with Session(engine) as session:
        usuarios = session.exec(select(Usuario)).all()
        if usuarios:
            return

        ana = Usuario(nombre="Ana López", usuario="ana01", correo="ana01@example.com", password="1234")
        juan = Usuario(nombre="Juan Pérez", usuario="juan_dev", correo="juan@example.com", password="1234")
        maria = Usuario(nombre="María Arteaga", usuario="maria_art", correo="maria@example.com", password="1234")

        session.add(ana)
        session.add(juan)
        session.add(maria)
        session.commit()
        session.refresh(ana)
        session.refresh(juan)
        session.refresh(maria)

        publicaciones = [
            Publicacion(
                titulo="Idea de decoración",
                descripcion="Inspiración para decorar espacios con estilo sencillo.",
                imagen_url="https://picsum.photos/400/300?random=1",
                usuario_id=ana.id,
            ),
            Publicacion(
                titulo="Diseño moderno",
                descripcion="Propuesta visual con líneas limpias y colores neutros.",
                imagen_url="https://picsum.photos/400/300?random=2",
                usuario_id=juan.id,
            ),
            Publicacion(
                titulo="Espacios verdes",
                descripcion="Ideas para integrar naturaleza y diseño interior.",
                imagen_url="https://picsum.photos/400/300?random=3",
                usuario_id=maria.id,
            ),
            Publicacion(
                titulo="Mi sala favorita",
                descripcion="Publicación de ejemplo para el perfil de Ana.",
                imagen_url="https://picsum.photos/400/300?random=11",
                usuario_id=ana.id,
            ),
            Publicacion(
                titulo="Ideas de cocina",
                descripcion="Inspiración para organizar una cocina pequeña.",
                imagen_url="https://picsum.photos/400/300?random=12",
                usuario_id=ana.id,
            ),
        ]

        for publicacion in publicaciones:
            session.add(publicacion)
        session.commit()

        primera_publicacion = session.exec(select(Publicacion).where(Publicacion.titulo == "Idea de decoración")).first()
        tercera_publicacion = session.exec(select(Publicacion).where(Publicacion.titulo == "Espacios verdes")).first()

        comentarios = [
            Comentario(autor="ana01", contenido="Muy bonito diseño.", publicacion_id=tercera_publicacion.id),
            Comentario(autor="juan_dev", contenido="Me gusta la combinación de colores.", publicacion_id=tercera_publicacion.id),
            Comentario(autor="carla", contenido="Lo guardaré para inspiración.", publicacion_id=tercera_publicacion.id),
            Comentario(autor="maria_art", contenido="Excelente idea.", publicacion_id=primera_publicacion.id),
        ]

        for comentario in comentarios:
            session.add(comentario)
        session.commit()


@asynccontextmanager
async def create_all_table(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    seed_data()
    yield


def get_session():
    with Session(engine) as session:
        yield session
