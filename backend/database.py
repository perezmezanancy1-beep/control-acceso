import firebase_admin
from firebase_admin import credentials, firestore
import json
import os

# ✅ Inicializar Firebase correctamente
if not firebase_admin._apps:

    if "FIREBASE_CREDENTIALS" in os.environ:
        # ✅ Producción (Render)
        cred_dict = json.loads(os.environ["FIREBASE_CREDENTIALS"])
        cred = credentials.Certificate(cred_dict)
    else:
        # ✅ LOCAL (TU PC)
        cred = credentials.Certificate(
            r"C:\Users\PC HP 14-DY0005LA\OneDrive - UNIVERSIDAD AUTONOMA DEL CARIBE\Desktop\control_acceso\backend\serviceAccountKey.json"
        )

    firebase_admin.initialize_app(cred)

# ✅ Conexión a Firestore
db = firestore.client()
