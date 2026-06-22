from fastapi import HTTPException
import re
import unicodedata


PALABRAS_BLOQUEADAS = [
    "odio",
    "matar",
    "asesinar",
    "violencia",
    "racista",
    "discriminacion",
    "discriminación",
    "pornografia",
    "pornografía",
    "porno",
    "desnudo",
    "suicidio",
    "droga",
    "hackear",

    # Lenguaje ofensivo o irrespetuoso
    "mierda",
    "idiota",
    "estupido",
    "estúpido",
    "imbecil",
    "imbécil",
    "pendejo",
    "pendeja",
    "puta",
    "puto",
    "maldito",
    "basura",
]


def normalizar_texto(texto: str) -> str:
    texto = texto or ""
    texto = texto.lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return texto


def validar_texto_etico(*textos: str):
    texto_completo = " ".join(str(t or "") for t in textos).strip()

    if not texto_completo:
        return

    texto_normalizado = normalizar_texto(texto_completo)

    for palabra in PALABRAS_BLOQUEADAS:
        palabra_normalizada = normalizar_texto(palabra)
        patron = r"\b" + re.escape(palabra_normalizada) + r"\b"

        if re.search(patron, texto_normalizado):
            raise HTTPException(
                status_code=400,
                detail="Contenido bloqueado por política de contenido. Revisa las normas de la plataforma.",
            )


def validar_motivo_denuncia(motivo: str):
    if not motivo or len(motivo.strip()) < 5:
        raise HTTPException(
            status_code=400,
            detail="El motivo de la denuncia debe tener al menos 5 caracteres.",
        )

    validar_texto_etico(motivo)
