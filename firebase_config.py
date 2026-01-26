import os
import json
import firebase_admin
from firebase_admin import credentials, firestore, auth
from dotenv import load_dotenv

load_dotenv()

def init_firebase():
    """
    Initialise la connexion à Firebase.
    Récupère les identifiants depuis la variable d'environnement JSON pour la sécurité.
    """
    try:
        if not firebase_admin._apps:
            # Priorité 1 : Variable d'environnement (Production Render/Railway)
            firebase_creds_json = os.getenv("FIREBASE_CREDENTIALS")
            
            if firebase_creds_json:
                print("🔐 Chargement des identifiants Firebase depuis ENV...")
                creds_dict = json.loads(firebase_creds_json)
                cred = credentials.Certificate(creds_dict)
                firebase_admin.initialize_app(cred)
            else:
                # Priorité 2 : Fichier local (Développement)
                cred_path = "serviceAccountKey.json"
                if os.path.exists(cred_path):
                    print("📂 Chargement des identifiants Firebase depuis fichier local...")
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)
                else:
                    print("⚠️ Aucun identifiant trouvé. Mode simulation active.")
                    firebase_admin.initialize_app()
        
        return firestore.client()
    except Exception as e:
        print(f"❌ Erreur d'initialisation Firebase : {e}")
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
