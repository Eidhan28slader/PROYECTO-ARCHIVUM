from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

from app.routers import comentarios, denuncias, publicaciones, usuarios
from db import create_all_table


app = FastAPI(
    title="Archivum API",
    description="Backend del proyecto integrador con FastAPI, SQLite, SQLModel, AWS S3 y mecanismos éticos verificables.",
    version="2.1.0",
    lifespan=create_all_table,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5000",
        "http://127.0.0.1:5500",
        "http://localhost:5000",
        "http://localhost:5500",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://52.91.130.96:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(usuarios.router)
app.include_router(publicaciones.router)
app.include_router(comentarios.router)
app.include_router(denuncias.router)


@app.get("/")
def root():
    return {
        "message": "API de Archivum funcionando",
        "frontend": "/frontend/index.html",
        "docs": "/docs",
        "etica": "/frontend/normas.html",
    }


BASE_DIR = Path(__file__).resolve().parent
app.mount("/frontend", StaticFiles(directory="."), name="frontend")
