from fastapi import FastAPI
from backend.database import db
from backend.models import Persona
import uuid

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

app = FastAPI(title="Sistema de Control de Acceso")

BASE_DIR = Path(__file__).resolve().parent

#  Servir frontend
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "../frontend")), name="static")


#  Página principal
@app.get("/")
def index():
    return FileResponse(str(BASE_DIR / "../frontend/acceso.html"))


#  Buscar usuario
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

    qr_id = f"QR-{uuid.uuid4().hex[:6].upper()}"

    data = persona.dict()
    data["qr_id"] = qr_id
    data["dentro"] = False

    db.collection("personas").document(persona.cedula).set(data)

    return {
        "mensaje": "Persona registrada correctamente",
        "qr_id": qr_id,
        "cedula": persona.cedula
    }


#  VALIDAR ACCESO (ENTRADA)
@app.post("/acceso")
def validar_acceso(data: dict):

    qr_data = data.get("qr_id")

    if not qr_data:
        return {"permitido": False, "mensaje": "QR vacío"}

    #  SOPORTE PARA QR DINÁMICO
    try:
        qr_id = qr_data.split("|")[0].strip().upper()
    except:
        return {"permitido": False, "mensaje": "QR inválido"}

    if not qr_id.startswith("QR-"):
        return {"permitido": False, "mensaje": "QR inválido"}

    #  Buscar en Firebase
    personas = db.collection("personas").where("qr_id", "==", qr_id).stream()

    for persona in personas:
        datos = persona.to_dict()

        #  si no está activo
        if not datos.get("activo", True):
            return {
                "permitido": False,
                "mensaje": "Usuario inactivo"
            }

        # si ya está dentro
        if datos.get("dentro") == True:
            return {
                "permitido": False,
                "mensaje": f"{datos.get('nombres')} ya está dentro"
            }

        #  permitir entrada
        persona.reference.update({"dentro": True})

        return {
            "permitido": True,
            "mensaje": f"Acceso permitido: {datos.get('nombres')}"
        }

    return {"permitido": False, "mensaje": "QR no registrado"}


#  REGISTRAR SALIDA
@app.post("/salida")
def registrar_salida(data: dict):

    qr_data = data.get("qr_id")

    if not qr_data:
        return {"mensaje": "QR vacío"}

    try:
        qr_id = qr_data.split("|")[0].strip().upper()
    except:
        return {"mensaje": "QR inválido"}

    personas = db.collection("personas").where("qr_id", "==", qr_id).stream()

    for persona in personas:
        datos = persona.to_dict()

        # marcar salida
        persona.reference.update({"dentro": False})

        return {
            "mensaje": f"Salida registrada: {datos.get('nombres')}"
        }

    return {"mensaje": "QR no registrado"}
