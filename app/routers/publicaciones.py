import os
import time
import boto3
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from db import get_session
from models import Comentario, Publicacion, PublicacionCreate, PublicacionUpdate, Usuario

router = APIRouter(prefix="/publicaciones", tags=["publicaciones"])

# Inicializar el cliente de AWS S3 usando las variables de entorno del .env
s3_client = None
try:
    s3_client = boto3.client(
        's3',
        region_name=os.getenv('AWS_REGION'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
except Exception as e:
    print(f"Advertencia: No se pudo conectar a AWS S3: {e}")
    s3_client = None


def publicacion_con_usuario(publicacion: Publicacion, session: Session):
    usuario = session.get(Usuario, publicacion.usuario_id)
    return {
        "id": publicacion.id,
        "titulo": publicacion.titulo,
        "descripcion": publicacion.descripcion,
        "imagen_url": publicacion.imagen_url,
        "archivo_url": publicacion.archivo_url,
        "archivo_nombre": publicacion.archivo_nombre,
        "usuario_id": publicacion.usuario_id,
        "usuario": usuario.usuario if usuario else "desconocido",
        "nombre_usuario": usuario.nombre if usuario else "Usuario desconocido",
    }


# ==========================================
# NUEVA RUTA: GENERAR URL FIRMADA PARA AWS S3
# ==========================================
@router.get("/obtener-url-subida")
def obtener_url_subida():
    if not s3_client:
        raise HTTPException(status_code=503, detail="Servicio de almacenamiento no disponible")
    
    bucket_name = os.getenv('AWS_BUCKET_NAME')
    if not bucket_name:
        raise HTTPException(status_code=500, detail="Falta configurar las variables de entorno de AWS")
        
    # Generamos un nombre único usando timestamp para evitar que se pisen imágenes
    nombre_archivo = f"pin-{int(time.time())}.jpg"
    
    try:
        # Generar la URL firmada (vence en 3 minutos)
        url_firmada = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': nombre_archivo,
                'ContentType': 'image/jpeg'
            },
            ExpiresIn=180
        )
        
        # URL final con la que los demás usuarios verán la foto en el feed
        url_final_imagen = f"https://{bucket_name}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{nombre_archivo}"
        
        return {
            "urlFirmada": url_firmada,
            "urlFinalImagen": url_final_imagen
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar con AWS S3: {str(e)}")


# ==========================================
# RUTAS ORIGINALES DE TU CRUD
# ==========================================

@router.get("/")
def get_publicaciones(session: Session = Depends(get_session)):
    publicaciones = session.exec(select(Publicacion).order_by(Publicacion.id.desc())).all()
    return [publicacion_con_usuario(publicacion, session) for publicacion in publicaciones]


@router.post("/", status_code=201)
def create_publicacion(publicacion: PublicacionCreate, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, publicacion.usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    nueva_publicacion = Publicacion.model_validate(publicacion)
    session.add(nueva_publicacion)
    session.commit()
    session.refresh(nueva_publicacion)
    return publicacion_con_usuario(nueva_publicacion, session)


@router.get("/usuario/{usuario_id}")
def get_publicaciones_by_usuario(usuario_id: int, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    publicaciones = session.exec(
        select(Publicacion).where(Publicacion.usuario_id == usuario_id).order_by(Publicacion.id.desc())
    ).all()
    return [publicacion_con_usuario(publicacion, session) for publicacion in publicaciones]


@router.get("/{id}")
def get_publicacion_by_id(id: int, session: Session = Depends(get_session)):
    publicacion = session.get(Publicacion, id)
    if not publicacion:
        raise HTTPException(status_code=404, detail="Publicación no encontrada")
    return publicacion_con_usuario(publicacion, session)


@router.put("/{id}")
def update_publicacion(id: int, cambios: PublicacionUpdate, session: Session = Depends(get_session)):
    publicacion = session.get(Publicacion, id)
    if not publicacion:
        raise HTTPException(status_code=404, detail="Publicación no encontrada")

    datos = cambios.model_dump(exclude_unset=True)
    for campo, valor in datos.items():
        if valor is not None and str(valor).strip() != "":
            setattr(publicacion, campo, valor)

    session.add(publicacion)
    session.commit()
    session.refresh(publicacion)
    return publicacion_con_usuario(publicacion, session)


@router.delete("/{id}")
def delete_publicacion(id: int, session: Session = Depends(get_session)):
    publicacion = session.get(Publicacion, id)
    if not publicacion:
        raise HTTPException(status_code=404, detail="Publicación no encontrada")

    comentarios = session.exec(select(Comentario).where(Comentario.publicacion_id == id)).all()
    for comentario in comentarios:
        session.delete(comentario)

    session.delete(publicacion)
    session.commit()
    return {"message": "Publicación eliminada correctamente"}