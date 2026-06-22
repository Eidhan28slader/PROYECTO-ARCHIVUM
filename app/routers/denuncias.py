from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from db import get_session
from models import Denuncia, DenunciaCreate, Publicacion, Usuario
from app.etica import validar_motivo_denuncia


router = APIRouter(prefix="/denuncias", tags=["denuncias"])


@router.post("/", status_code=201)
def crear_denuncia(denuncia: DenunciaCreate, session: Session = Depends(get_session)):
    publicacion = session.get(Publicacion, denuncia.publicacion_id)
    if not publicacion:
        raise HTTPException(status_code=404, detail="Publicación no encontrada")

    usuario = session.get(Usuario, denuncia.usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    validar_motivo_denuncia(denuncia.motivo)

    nueva_denuncia = Denuncia.model_validate(denuncia)
    session.add(nueva_denuncia)
    session.commit()
    session.refresh(nueva_denuncia)

    return {
        "message": "Denuncia registrada correctamente. El contenido será revisado.",
        "denuncia": nueva_denuncia,
    }


@router.get("/")
def listar_denuncias(session: Session = Depends(get_session)):
    denuncias = session.exec(select(Denuncia).order_by(Denuncia.id.desc())).all()
    return denuncias
