from fastapi import FastAPI
from backend.database import db
from backend.models import Persona
import uuid

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from datetime import datetime

app = FastAPI(title="Sistema de Control de Acceso")

BASE_DIR = Path(__file__).resolve().parent

#  Servir frontend
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "../frontend")), name="static")


#  Página principal
@app.get("/")
def index():
    return FileResponse(str(BASE_DIR / "../frontend/acceso.html"))


#  Buscar usuario por cédula
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


#  Registrar persona
@app.post("/personas")
def crear_persona(persona: Persona):

    qr_id = f"QR-{uuid.uuid4().hex[:8].upper()}"

    data = persona.dict()
    data["qr_id"] = qr_id
    data["dentro"] = False

    db.collection("personas").document(persona.cedula).set(data)

    return {
        "mensaje": "Persona registrada correctamente",
        "qr_id": qr_id,
        "cedula": persona.cedula
    }


#  VALIDACIÓN DE ACCESO (ESTE ERA EL CLAVE)
@app.post("/acceso")
def validar_acceso(data: dict):

    qr_data = data.get("qr_id")

    if not qr_data:
        return {
            "permitido": False,
            "mensaje": "QR vacío"
        }

    # Extraer el código (por si viene con |timestamp)
    qr_id = qr_data[:11]
    if not qr_id.startswith("QR-"):
        return {"permitido":False, "mensaje": "QR inválido"}

    # Buscar en Firebase
    personas = db.collection("personas").where("qr_id", "==", qr_id).stream()

    for persona in personas:
        datos = persona.to_dict()

        return {
            "permitido": True,
            "mensaje": f"Acceso permitido: {datos.get('nombres')}"
        }

    return {
        "permitido": False,
        "mensaje": "QR no registrado"
    }

