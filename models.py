from sqlmodel import Field, SQLModel


class Usuario(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    usuario: str = Field(index=True)
    correo: str = Field(index=True)
    password: str


class UsuarioCreate(SQLModel):
    nombre: str
    usuario: str
    correo: str
    password: str


class UsuarioLogin(SQLModel):
    usuario_o_correo: str
    password: str


class Publicacion(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    titulo: str
    descripcion: str
    imagen_url: str
    archivo_url: str | None = None
    archivo_nombre: str | None = None
    usuario_id: int = Field(foreign_key="usuario.id")


class PublicacionCreate(SQLModel):
    titulo: str
    descripcion: str
    imagen_url: str | None = None
    archivo_url: str | None = None
    archivo_nombre: str | None = None
    usuario_id: int


class PublicacionUpdate(SQLModel):
    titulo: str | None = None
    descripcion: str | None = None
    imagen_url: str | None = None
    archivo_url: str | None = None
    archivo_nombre: str | None = None


class Comentario(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    autor: str
    contenido: str
    publicacion_id: int = Field(foreign_key="publicacion.id")


class ComentarioCreate(SQLModel):
    autor: str
    contenido: str
    publicacion_id: int
