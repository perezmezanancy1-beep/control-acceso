import firebase_admin
from firebase_admin import credentials, firestore
import json
import os

# ✅ Inicializar Firebase correctamente en Render
if not firebase_admin._apps:

    if "FIREBASE_CREDENTIALS" in os.environ:
        # Render / Producción
        cred_dict = json.loads(os.environ["FIREBASE_CREDENTIALS"])
        cred = credentials.Certificate(cred_dict)
    else:
        # Local
        cred = credentials.Certificate("serviceAccountKey.json")

    firebase_admin.initialize_app(cred)

db = firestore.client()
