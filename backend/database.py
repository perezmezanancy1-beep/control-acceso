import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path

# Obtener la ruta absoluta de la carpeta backend
BASE_DIR = Path(__file__).resolve().parent
KEY_PATH = BASE_DIR / "firebase_key.json"

cred = credentials.Certificate(str(KEY_PATH))
firebase_admin.initialize_app(cred)

db = firestore.client()
