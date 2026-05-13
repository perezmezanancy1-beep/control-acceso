from fastapi import FastAPI
from backend.database import db
from backend.models import Persona
import uuid

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

app = FastAPI(title="Sistema de Control de Acceso")

BASE_DIR = Path(__file__).resolve().parent

# Servir frontend
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "../frontend")), name="static")

@app.get("/")
def index():
    return FileResponse(str(BASE_DIR / "../frontend/acceso.html"))

# ✅ Buscar usuario por cédula (página pública)
@app.get("/buscar_usuario")
def buscar_usuario(nombre: str):
    doc = db.collection("personas").document(nombre).get()
    if doc.exists:
        datos = doc.to_dict()
        return {
            "encontrado": True,
            "qr_id": datos.get("qr_id"),
            "nombre": datos.get("nombres", "")
        }
    return {"encontrado": False}

# ✅ Registro administrativo (GUARDA EN FIREBASE Y DEVUELVE QR)
@app.post("/personas")
def crear_persona(persona: Persona):
    qr_id = f"QR-{uuid.uuid4().hex[:8].upper()}"

    data = persona.dict()
    data["qr_id"] = qr_id
    data["dentro"] = False

    # Usar la cédula como ID del documento
    db.collection("personas").document(persona.cedula).set(data)

    return {
        "mensaje": "Persona registrada",
        "qr_id": qr_id,
        "cedula": persona.cedula
    }

