from fastapi import FastAPI
from backend.database import db
from datetime import datetime
import time

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

app = FastAPI(title="Sistema de Control de Acceso")

# ✅ RUTA BASE
BASE_DIR = Path(__file__).resolve().parent

# ✅ SERVIR ARCHIVOS ESTÁTICOS
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "../frontend")), name="static")

# ✅ ABRIR PÁGINA PRINCIPAL
@app.get("/")
def index():
    return FileResponse(str(BASE_DIR / "../frontend/acceso.html"))

# ✅ PERMITIR CARGAR OTROS HTML (como qr_dinamico.html)
@app.get("/{file_name}")
def serve_file(file_name: str):
    file_path = BASE_DIR / "../frontend" / file_name
    if file_path.exists():
        return FileResponse(str(file_path))
    return {"error": "Archivo no encontrado"}

# ✅ TIEMPO DEL QR
QR_TIEMPO_MAX = 30


# ✅ BUSCAR USUARIO POR CÉDULA (USANDO ID DEL DOCUMENTO 🔥)
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


# ✅ VALIDAR QR DINÁMICO
def validar_qr_dinamico(qr_completo: str):
    try:
        partes = qr_completo.split("|")

        if len(partes) < 2:
            return False, None

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

        if str(datos.get("qr_id")).strip().upper() == qr_id:

            if not datos.get("dentro"):

                personas_ref.document(doc.id).update({
                    "dentro": True
                })

                return {
                    "permitido": True,
                    "accion": "entrada",
                    "mensaje": "Entrada permitida"
                }

            else:

                personas_ref.document(doc.id).update({
                    "dentro": False
                })

                return {
                    "permitido": True,
                    "accion": "salida",
                    "mensaje": "Salida registrada"
                }

    return {"permitido": False}
