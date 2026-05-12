from fastapi import FastAPI
from backend.database import db
from datetime import datetime
import time

app = FastAPI()

QR_TIEMPO_MAX = 30


# ✅ BUSCAR USUARIO POR CÉDULA (VERSIÓN SEGURA)
@app.get("/buscar_usuario")
def buscar_usuario(nombre: str):

    print("Buscando cédula:", nombre)  # DEBUG

    personas_ref = db.collection("personas")

    for doc in personas_ref.stream():
        datos = doc.to_dict()

        print("Comparando con:", datos.get("cedula"))  # DEBUG

        if str(datos.get("cedula")) == str(nombre):
            print("✅ ENCONTRADO")

            return {
                "encontrado": True,
                "qr_id": datos.get("qr_id"),
                "nombre": datos.get("nombres", "")
            }

    print("❌ NO ENCONTRADO")
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
        return {"permitido": False}

    valido, qr_id, _ = validar_qr_dinamico(qr_completo)

    if not valido:
        return {"permitido": False}

    qr_id = qr_id.strip().upper()

    personas_ref = db.collection("personas")

    for doc in personas_ref.stream():
        datos = doc.to_dict()

        if str(datos.get("qr_id")).strip().upper() == qr_id:

            if not datos.get("dentro"):

                personas_ref.document(doc.id).update({"dentro": True})

                return {"permitido": True, "accion": "entrada"}

            else:

                personas_ref.document(doc.id).update({"dentro": False})

                return {"permitido": True, "accion": "salida"}

    return {"permitido": False}