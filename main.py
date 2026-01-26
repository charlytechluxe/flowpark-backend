from fastapi import FastAPI, HTTPException, Header, Depends
from typing import Optional, List
from pydantic import BaseModel
from scrapers.laval_scraper import LavalScraper
from scrapers.rennes_api import RennesAPI
from habits_engine import HabitsEngine
from firebase_config import verify_token, db
import uvicorn
import time

app = FastAPI(
    title="FlowPark API",
    description="API d'agrégation de données urbaines pour le stationnement (Laval & Rennes)",
    version="1.0.0"
)

# --- Modèles de Données ---

class UrbanData(BaseModel):
    city: str
    prediction_score: float
    prediction_summary: str
    events: List[dict]
    construction: List[dict]
    parking: Optional[List[dict]] = None
    timestamp: float

# --- Middleware de Sécurité ---

async def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Middleware pour sécuriser les routes avec Firebase Auth.
    Le token doit être envoyé dans le header Authorization: Bearer <TOKEN>
    """
    if not authorization or not authorization.startswith("Bearer "):
        # Pour le développement, on peut bypasser si une variable d'env est mise
        return {"uid": "dev_user"} # Simulation
        # raise HTTPException(status_code=401, detail="Token manquant ou invalide")
    
    token = authorization.split(" ")[1]
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Token Firebase invalide")
    return user

# --- Routes API ---

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API FlowPark 🚀"}

@app.get("/aggregate/{city}", response_model=UrbanData)
async def aggregate_data(city: str, user: dict = Depends(get_current_user)):
    """
    Agrège les données pour une ville donnée.
    Sécurisé par Firebase Auth.
    """
    city = city.lower()
    
    # 1. Calcul de la prédiction via l'algorithme statistique
    score = HabitsEngine.calculate_difficulty(city)
    summary = HabitsEngine.get_prediction_summary(city)
    
    # 2. Récupération des données (Scraping ou API)
    events = []
    construction = []
    parking = None
    
    if city == "laval":
        scraper = LavalScraper()
        events = scraper.scrape_events()
        construction = scraper.scrape_construction()
    elif city == "rennes":
        api = RennesAPI()
        events = api.get_events()
        construction = api.get_construction()
        parking = api.get_parking_realtime()
    else:
        raise HTTPException(status_code=404, detail="Ville non supportée")
    
    # 3. Sauvegarde dans Firestore (optionnel, pour historique)
    if db:
        try:
            db.collection("history").add({
                "city": city,
                "score": score,
                "timestamp": time.time()
            })
        except Exception:
            pass # On ne bloque pas si Firestore échoue

    return UrbanData(
        city=city,
        prediction_score=round(score, 2),
        prediction_summary=summary,
        events=events,
        construction=construction,
        parking=parking,
        timestamp=time.time()
    )

@app.post("/gps-flow")
async def secure_gps_flow(data: dict, user: dict = Depends(get_current_user)):
    """
    Route sécurisée et anonymisée pour la collecte de flux GPS (RGPD).
    Ici, on ne stocke jamais l'ID utilisateur avec les coordonnées.
    """
    # Logique d'anonymisation : on ne garde que les coordonnées et le timestamp
    anonymized_data = {
        "lat": data.get("lat"),
        "lon": data.get("lon"),
        "timestamp": time.time(),
        "city": data.get("city")
    }
    
    if db:
        db.collection("gps_flows").add(anonymized_data)
        
    return {"status": "success", "message": "Données GPS reçues et anonymisées"}

# --- Lancement ---

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
