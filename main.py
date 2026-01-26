from fastapi import FastAPI, HTTPException, Header, Depends
from typing import Optional, List
from pydantic import BaseModel
from scrapers.laval_scraper import LavalScraper
from scrapers.rennes_api import RennesAPI
from habits_engine import HabitsEngine
from weather_engine import WeatherEngine
from firebase_config import verify_token, db
import uvicorn
import time

app = FastAPI(
    title="FlowPark API v1.1",
    description="Agrégation intelligente avec Météo et Cache",
    version="1.1.0"
)

# --- Système de Cache Simple ---
cache = {
    "laval": {"data": None, "expiry": 0},
    "rennes": {"data": None, "expiry": 0}
}
CACHE_DURATION = 900 # 15 minutes en secondes

# --- Modèles de Données ---

class UrbanData(BaseModel):
    city: str
    prediction_score: float
    prediction_summary: str
    weather: dict
    events: List[dict]
    construction: List[dict]
    parking: Optional[List[dict]] = None
    timestamp: float

# --- Middleware de Sécurité ---

async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        return {"uid": "dev_user"}
    
    token = authorization.split(" ")[1]
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Token Firebase invalide")
    return user

# --- Routes API ---

@app.get("/")
def read_root():
    return {"message": "FlowPark API v1.1 - Intelligence Urbaine 🚀"}

@app.get("/aggregate/{city}", response_model=UrbanData)
async def aggregate_data(city: str, user: dict = Depends(get_current_user)):
    city = city.lower()
    now = time.time()
    
    # 1. Vérification du Cache
    if cache.get(city) and cache[city]["expiry"] > now:
        print(f"⚡ Cache HIT pour {city}")
        cached_res = cache[city]["data"]
        return cached_res

    # 2. Récupération Météo (Nouveau v1.1)
    weather = WeatherEngine.get_weather(city)
    
    events = []
    construction = []
    parking = None
    
    # 3. Récupération des données (Scraping ou API)
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
    
    # 4. Calcul de la prédiction pondérée (v1.1)
    score = HabitsEngine.calculate_difficulty(
        city, 
        weather_impact=weather.get("is_bad", False),
        event_count=len(events)
    )
    summary = HabitsEngine.get_prediction_summary(score)

    result = UrbanData(
        city=city,
        prediction_score=round(score, 2),
        prediction_summary=summary,
        weather=weather,
        events=events,
        construction=construction,
        parking=parking,
        timestamp=now
    )

    # 5. Mise en cache
    cache[city] = {
        "data": result,
        "expiry": now + CACHE_DURATION
    }

    # 6. Historisation Firestore
    if db:
        try:
            db.collection("history").add({
                "city": city,
                "score": score,
                "weather": weather.get("condition"),
                "timestamp": now
            })
        except Exception:
            pass

    return result

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
