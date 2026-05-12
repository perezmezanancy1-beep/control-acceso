from fastapi import FastAPI
from backend.database import db
from datetime import datetime
import time

# ✅ SERVIR ARCHIVOS HTML
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

app = FastAPI(title="Sistema de Control de Acceso")

# ✅ RUTA BASE
BASE_DIR = Path(__file__).resolve().parent

# ✅ SERVIR ARCHIVOS ESTÁTICOS
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "../frontend")), name="static")

# ✅ PÁGINA PRINCIPAL (ARREGLA EL 404)
@app.get("/")
def index():
    return FileResponse(str(BASE_DIR / "../frontend/acceso.html"))


# ✅ TIEMPO DEL QR
QR_TIEMPO_MAX = 30


# ✅ BUSCAR USUARIO POR CÉDULA
@app.get("/buscar_usuario")
def buscar_usuario(nombre: str):

    personas_ref = db.collection("personas")

    for doc in personas_ref.stream():
        datos = doc.to_dict()

        if str(datos.get("cedula")) == str(nombre):
            return {
                "encontrado": True,
                "qr_id": datos.get("qr_id"),
                "nombre": datos.get("nombres", "")
            }

    return {"encontrado": False}


# ✅ VALIDAR QR
def validar_qr_dinamico(qr_completo: str):
    try:
        partes = qr_completo.split("|")

        if len(partes) < 2:
            return False, None, "Formato inválido"

        qr_base = partes[0].strip().upper()
        timestamp = int(partes[1])

        ahora = int(time.time())

        if ahora - timestamp > QR_TIEMPO_MAX:
            return False, None, "QR expirado"

        return True, qr_base, None

    except:
        return False, None, "QR inválido"


# ✅ CONTROL DE ACCESO
@app.post("/acceso")
def controlar_acceso(data: dict):

    qr_completo = data.get("qr_id")

    if not qr_completo:
        return {"permitido": False, "mensaje": "QR no enviado"}

    valido, qr_id, error = validar_qr_dinamico(qr_completo)

    if not valido:
        return {"permitido": False, "mensaje": error}

    qr_id = qr_id.strip().upper()

    personas_ref = db.collection("personas")

    persona = None

    for doc in personas_ref.stream():
        datos = doc.to_dict()

        if str(datos.get("qr_id", "")).strip().upper() == qr_id:
            persona = doc
            break

    if not persona:
        return {"permitido": False, "mensaje": "Persona no registrada"}

    datos = persona.to_dict()

    # ✅ ENTRADA / SALIDA
    if not datos.get("dentro"):

        personas_ref.document(persona.id).update({
            "dentro": True
        })

        return {
            "permitido": True,
            "accion": "entrada",
            "mensaje": "Entrada permitida"
        }

    else:

        personas_ref.document(persona.id).update({
            "dentro": False
        })

        return {
            "permitido": True,
            "accion": "salida",
            "mensaje": "Salida registrada"
        }
