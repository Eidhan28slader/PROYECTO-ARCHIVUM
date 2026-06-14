from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from db import get_session
from models import Usuario, UsuarioCreate, UsuarioLogin

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


def usuario_sin_password(usuario: Usuario):
    return {
        "id": usuario.id,
        "nombre": usuario.nombre,
        "usuario": usuario.usuario,
        "correo": usuario.correo,
    }


@router.get("/")
def get_usuarios(session: Session = Depends(get_session)):
    usuarios = session.exec(select(Usuario)).all()
    return [usuario_sin_password(usuario) for usuario in usuarios]


@router.get("/{id}")
def get_usuario_by_id(id: int, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario_sin_password(usuario)


@router.post("/", status_code=201)
def create_usuario(usuario: UsuarioCreate, session: Session = Depends(get_session)):
    usuario_existente = session.exec(
        select(Usuario).where((Usuario.usuario == usuario.usuario) | (Usuario.correo == usuario.correo))
    ).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="El usuario o correo ya existe")

    nuevo_usuario = Usuario.model_validate(usuario)
    session.add(nuevo_usuario)
    session.commit()
    session.refresh(nuevo_usuario)
    return usuario_sin_password(nuevo_usuario)


@router.post("/login")
def login(datos: UsuarioLogin, session: Session = Depends(get_session)):
    usuario = session.exec(
        select(Usuario).where(
            ((Usuario.usuario == datos.usuario_o_correo) | (Usuario.correo == datos.usuario_o_correo))
            & (Usuario.password == datos.password)
        )
    ).first()

    if not usuario:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    return usuario_sin_password(usuario)
