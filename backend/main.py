from fastapi import FastAPI
from backend.database import db
from datetime import datetime
import time

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

app = FastAPI(title="Sistema de Control de Acceso")

# -------------------------------
# CONFIGURACIÓN FRONTEND
# -------------------------------
BASE_DIR = Path(__file__).resolve().parent

# Servir archivos estáticos (css, js, imágenes)
app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "../frontend")),
    name="static"
)

# Página principal
@app.get("/")
def index():
    return FileResponse(str(BASE_DIR / "../frontend/acceso.html"))


# -------------------------------
# CONFIGURACIÓN QR
# -------------------------------
QR_TIEMPO_MAX = 30  # segundos


# -------------------------------
# BUSCAR USUARIO POR CÉDULA
# (ID del documento en Firestore)
# -------------------------------
@app.get("/buscar_usuario")
def buscar_usuario(nombre: str):

    # Buscar directamente por ID del documento
    doc = db.collection("personas").document(nombre).get()

    if doc.exists:
        datos = doc.to_dict()
        return {
            "encontrado": True,
            "qr_id": datos.get("qr_id"),
            "nombre": datos.get("nombres", "")
        }

    return {"encontrado": False}


# -------------------------------
# VALIDAR QR DINÁMICO
# -------------------------------
def validar_qr_dinamico(qr_completo: str):
    try:
        partes = qr_completo.split("|")

        if len(partes) < 2:
            return False, None

        qr_base = partes[0].strip().upper()
        timestamp = int(partes[1])

        # VALIDACIÓN DE TIEMPO (CORREGIDA)
        if int(time.time()) - timestamp > QR_TIEMPO_MAX:
            return False, None

        return True, qr_base

    except Exception:
        return False, None


# -------------------------------
# CONTROL DE ACCESO
# -------------------------------
@app.post("/acceso")
def controlar_acceso(data: dict):

    qr = data.get("qr_id")

    if not qr:
        return {"permitido": False, "mensaje": "QR no enviado"}

    valido, qr_id = validar_qr_dinamico(qr)

    if not valido:
        return {"permitido": False, "mensaje": "QR inválido o expirado"}

    personas_ref = db.collection("personas")

    # Buscar persona por qr_id
    for doc in personas_ref.stream():
        datos = doc.to_dict()

        if str(datos.get("qr_id", "")).strip().upper() == qr_id:

            if not datos.get("dentro"):
                # ENTRADA
                personas_ref.document(doc.id).update({
                    "dentro": True
                })

                return {
                    "permitido": True,
                    "accion": "entrada",
                    "mensaje": "Entrada permitida"
                }

            else:
                # SALIDA
                personas_ref.document(doc.id).update({
                    "dentro": False
                })

                return {
                    "permitido": True,
                    "accion": "salida",
                    "mensaje": "Salida registrada"
                }

    return {"permitido": False, "mensaje": "Persona no registrada"}
