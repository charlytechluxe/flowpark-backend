import os
import firebase_admin
from firebase_admin import credentials, firestore, auth
from dotenv import load_dotenv

load_dotenv()

# Note : Pour un déploiement réel, assurez-vous de configurer FIREBASE_SERVICE_ACCOUNT_JSON
# ou d'utiliser les variables d'environnement pour charger les identifiants.

CRED_PATH = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "serviceAccountKey.json")

def init_firebase():
    """
    Initialise la connexion à Firebase.
    Si le fichier de clé n'existe pas, on utilise une simulation pour le développement.
    """
    try:
        if not firebase_admin._apps:
            if os.path.exists(CRED_PATH):
                cred = credentials.Certificate(CRED_PATH)
                firebase_admin.initialize_app(cred)
            else:
                print("⚠️ Avis : serviceAccountKey.json non trouvé. Utilisation d'un mode restreint.")
                # En production, cela lèverait une erreur.
                # Pour cet exercice, on initialise sans identifiants si on est en local
                firebase_admin.initialize_app()
        
        return firestore.client()
    except Exception as e:
        print(f"Erreur d'initialisation Firebase : {e}")
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
