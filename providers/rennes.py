import requests
import logging
from .base import CityProvider

logger = logging.getLogger("flowpark.rennes")

class RennesProvider(CityProvider):
    BASE_URL = "https://data.rennesmetropole.fr/api/records/1.0/search/"
    
    def get_events(self):
        logger.info("Fetching events for Rennes via API...")
        try:
            params = {"dataset": "agenda-culturel-rennes-metropole", "rows": 10}
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            return [{"title": r["fields"].get("titre", "Sans titre"), "source": "Open Data"} for r in response.json().get("records", [])]
        except Exception as e:
            logger.error(f"Rennes API Error (Events): {e}")
            return []

    def get_construction(self):
        logger.info("Fetching construction for Rennes via API...")
        try:
            params = {"dataset": "geotravaux", "rows": 10}
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            return [{"location": r["fields"].get("nom_rue", "Inconnu"), "source": "Geotravaux"} for r in response.json().get("records", [])]
        except Exception as e:
            logger.error(f"Rennes API Error (Construction): {e}")
            return []

    def get_parking(self):
        logger.info("Fetching parking for Rennes via API...")
        try:
            params = {"dataset": "parking-rennes-metropole-temps-reel", "rows": 10}
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            return [{"name": r["fields"].get("nom"), "available": r["fields"].get("libre")} for r in response.json().get("records", [])]
        except Exception as e:
            logger.error(f"Rennes API Error (Parking): {e}")
            return []
