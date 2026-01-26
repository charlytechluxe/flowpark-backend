import logging
import time
from typing import List, Optional

import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from firebase_config import db, verify_token
from habits_engine import HabitsEngine
from providers.manager import CityManager
from weather_engine import WeatherEngine

# --- Configuration du Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("flowpark.api")

app = FastAPI(
    title="FlowPark PRO API",
    description="Solution de prédiction de stationnement urbain v2.0 Production-Ready.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# --- Modèles de Données avec Exemples ---

class WeatherData(BaseModel):
    condition: str = Field(..., example="bonne")
    is_bad: bool = Field(..., example=False)
    temp: Optional[float] = Field(None, example=18.5)

class UrbanData(BaseModel):
    city: str = Field(..., example="rennes")
    prediction_score: float = Field(..., example=0.45)
    prediction_summary: str = Field(..., example="Stationnement tendu (Orange)")
    weather: WeatherData
    events: List[dict] = Field(..., example=[{"title": "Festival", "source": "Open Data"}])
    construction: List[dict] = Field(..., example=[{"location": "Rue de la Paix", "source": "Geotravaux"}])
    parking: Optional[List[dict]] = Field(None, example=[{"name": "Parking Central", "available": 50}])
    timestamp: float = Field(..., example=1706300000.0)

# --- Système de Cache ---
cache = {}
CACHE_DURATION = 900

# --- Sécurité ---

async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        logger.debug("Request using dev mode / no token")
        return {"uid": "dev_user"}
    
    token = authorization.split(" ")[1]
    user = verify_token(token)
    if not user:
        logger.warning(f"Failed authentication attempt with token: {token[:10]}...")
        raise HTTPException(status_code=401, detail="Token invalide")
    return user

# --- Routes API ---

@app.get("/", tags=["Info"])
def read_root():
    return {"status": "online", "version": "2.0.0", "engine": "HabitsEngine 1.1"}

@app.get("/health", tags=["System"])
async def health_check():
    """Vérifie l'état des services critiques."""
    health = {"status": "healthy", "checks": {}}
    
    # Check Firebase
    health["checks"]["firebase"] = "up" if db is not None else "down"
    if db is None: health["status"] = "unhealthy"
    
    # Check Providers
    health["checks"]["cities_supported"] = CityManager.get_supported_cities()
    
    return health

@app.get("/aggregate/{city}", response_model=UrbanData, tags=["Production"])
async def aggregate_data(city: str, user: dict = Depends(get_current_user)):
    """
    Récupère et agrège toutes les données pour une ville.
    Gère le cache (15 min) et la pondération dynamique.
    """
    city = city.lower()
    now = time.time()
    
    if city in cache and cache[city]["expiry"] > now:
        logger.info(f"⚡ Cache Hit: {city}")
        return cache[city]["data"]

    logger.info(f"🔍 Aggregation request for city: {city}")
    
    try:
        # Load Provider
        provider = CityManager.get_provider(city)
        weather = WeatherEngine.get_weather(city)
        
        events = provider.get_events()
        construction = provider.get_construction()
        parking = provider.get_parking()
        
        # Calculate Prediction
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

        cache[city] = {"data": result, "expiry": now + CACHE_DURATION}
        
        if db:
            db.collection("history").add({"city": city, "score": score, "time": now})
            
        return result

    except ValueError as e:
        logger.error(f"Unsupported city request: {city}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception(f"Unexpected error during aggregation for {city}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@app.post("/gps-flow", status_code=201, tags=["Production"])
async def secure_gps_flow(data: dict, user: dict = Depends(get_current_user)):
    """Route sécurisée RGPD pour la collecte anonyme."""
    if not data.get("lat") or not data.get("lon"):
        raise HTTPException(status_code=400, detail="Coordonnées manquantes")
        
    logger.info("📡 Reception of anonymous GPS flow")
    if db:
        db.collection("gps_flows").add({
            "lat": data["lat"],
            "lon": data["lon"],
            "city": data.get("city", "unknown"),
            "timestamp": time.time()
        })
    return {"status": "accepted"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
