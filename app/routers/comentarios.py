from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from db import get_session
from models import Comentario, ComentarioCreate, Publicacion
from app.etica import validar_texto_etico


router = APIRouter(prefix="/comentarios", tags=["comentarios"])


@router.get("/publicacion/{publicacion_id}")
def get_comentarios(publicacion_id: int, session: Session = Depends(get_session)):
    publicacion = session.get(Publicacion, publicacion_id)
    if not publicacion:
        raise HTTPException(status_code=404, detail="Publicación no encontrada")

    return session.exec(
        select(Comentario)
        .where(Comentario.publicacion_id == publicacion_id)
        .order_by(Comentario.id.desc())
    ).all()


@router.post("/", status_code=201)
def create_comentario(comentario: ComentarioCreate, session: Session = Depends(get_session)):
    publicacion = session.get(Publicacion, comentario.publicacion_id)
    if not publicacion:
        raise HTTPException(status_code=404, detail="Publicación no encontrada")

    if not comentario.contenido.strip():
        raise HTTPException(status_code=400, detail="El comentario no puede estar vacío")

    validar_texto_etico(comentario.autor, comentario.contenido)

    nuevo_comentario = Comentario.model_validate(comentario)
    session.add(nuevo_comentario)
    session.commit()
    session.refresh(nuevo_comentario)

    return nuevo_comentario


@router.delete("/{id}")
def delete_comentario(id: int, session: Session = Depends(get_session)):
    comentario = session.get(Comentario, id)
    if not comentario:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")

    session.delete(comentario)
    session.commit()

    return {"message": "Comentario eliminado correctamente"}
