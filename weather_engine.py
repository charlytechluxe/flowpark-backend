import requests
import os

class WeatherEngine:
    """
    Récupère la météo en temps réel pour influencer la difficulté de stationnement.
    Utilise l'API Open-Meteo (gratuite et sans clé pour démonstration).
    """
    
    # Coordonnées approximatives
    CITIES = {
        "laval": {"lat": 48.07, "lon": -0.77},
        "rennes": {"lat": 48.11, "lon": -1.67}
    }

    @staticmethod
    def get_weather(city_name: str):
        """
        Récupère l'état météo actuel (pluie, neige, ciel dégagé).
        """
        city_name = city_name.lower()
        if city_name not in WeatherEngine.CITIES:
            return {"condition": "unknown", "is_bad": False}

        coords = WeatherEngine.CITIES[city_name]
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={coords['lat']}&longitude={coords['lon']}&current_weather=true"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            weather_code = data.get("current_weather", {}).get("weathercode", 0)
            
            # Codes Open-Meteo pour pluie/neige/orage (> 50)
            # https://open-meteo.com/en/docs
            is_bad = weather_code > 50
            
            return {
                "condition": "mauvaise" if is_bad else "bonne",
                "is_bad": is_bad,
                "temp": data.get("current_weather", {}).get("temperature")
            }
        except Exception as e:
            print(f"🌦️ Erreur météo pour {city_name}: {e}")
            return {"condition": "unknown", "is_bad": False, "temp": None}
