import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

# ==============================
#  CONFIGURACIÓN DE FIREBASE
# ==============================

def inicializar_firebase():
    """
    Inicializa Firebase de forma segura en:
    - Local (PC o Raspberry)
    - Producción (Render / nube)
    """

    if firebase_admin._apps:
        return firestore.client()

    try:
        #  1. Producción (Render / variables de entorno)
        if "FIREBASE_CREDENTIALS" in os.environ:
            cred_dict = json.loads(os.environ["FIREBASE_CREDENTIALS"])
            cred = credentials.Certificate(cred_dict)

        #  2. Local (Raspberry o PC)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            cred_path = os.path.join(base_dir, "serviceAccountKey.json")

            if not os.path.exists(cred_path):
                raise FileNotFoundError(
                    "❌ No se encontró el archivo serviceAccountKey.json en backend/"
                )

            cred = credentials.Certificate(cred_path)

        firebase_admin.initialize_app(cred)

        print("✅ Firebase conectado correctamente")
        return firestore.client()

    except Exception as e:
        print("❌ Error al conectar con Firebase:")
        print(e)
        raise


# ==============================
# INSTANCIA GLOBAL DE DB
# ==============================

db = inicializar_firebase()
