import os
import json
import logging
import firebase_admin
from firebase_admin import credentials, firestore, auth
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("flowpark.firebase")

def init_firebase():
    try:
        if not firebase_admin._apps:
            firebase_creds_json = os.getenv("FIREBASE_CREDENTIALS")
            if firebase_creds_json:
                logger.info("🔐 Initialisation Firebase via variable d'environnement.")
                creds_dict = json.loads(firebase_creds_json)
                cred = credentials.Certificate(creds_dict)
                firebase_admin.initialize_app(cred)
            else:
                cred_path = "serviceAccountKey.json"
                if os.path.exists(cred_path):
                    logger.info("📂 Initialisation Firebase via fichier local.")
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)
                else:
                    logger.warning("⚠️ Mode de simulation Firebase (données locales uniquement).")
                    firebase_admin.initialize_app()
        return firestore.client()
    except Exception as e:
        logger.error(f"❌ Échec de la connexion Firebase : {e}")
        return None

db = init_firebase()

def verify_token(id_token: str):
    """
    Vérifie le token Firebase Auth envoyé par l'application iOS.
    """
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception:
        return None
