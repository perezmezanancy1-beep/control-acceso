from fastapi import FastAPI
from backend.database import db
from datetime import datetime
import time

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

app = FastAPI(title="Sistema de Control de Acceso")

BASE_DIR = Path(__file__).resolve().parent

# ✅ Servir frontend
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "../frontend")), name="static")

@app.get("/")
def index():
    return FileResponse(str(BASE_DIR / "../frontend/acceso.html"))

# ✅ Tiempo QR
QR_TIEMPO_MAX = 30


# ✅ BUSCAR USUARIO (ESTA RUTA YA NO LA PISA NADIE)
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


# ✅ VALIDAR QR
def validar_qr_dinamico(qr_completo: str):
    try:
        partes = qr_completo.split("|")
        qr_base = partes[0].strip().upper()
        timestamp = int(partes[1])

        if int(time.time()) - timestamp > QR_TIEMPO_MAX:
            return False, None

        return True, qr_base
    except:
        return False, None


# ✅ CONTROL DE ACCESO
@app.post("/acceso")
def acceso(data: dict):

    qr = data.get("qr_id")
    valido, qr_id = validar_qr_dinamico(qr)

    if not valido:
        return {"permitido": False}

    personas_ref = db.collection("personas")

    for doc in personas_ref.stream():
        datos = doc.to_dict()

        if datos.get("qr_id") == qr_id:

            if not datos.get("dentro"):
                personas_ref.document(doc.id).update({"dentro": True})
                return {"permitido": True, "accion": "entrada"}

            else:
                personas_ref.document(doc.id).update({"dentro": False})
                return {"permitido": True, "accion": "salida"}

    return {"permitido": False}
