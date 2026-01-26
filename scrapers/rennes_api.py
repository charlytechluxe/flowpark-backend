import requests

class RennesAPI:
    """
    Client pour l'Open Data de Rennes Métropole.
    Utilise les API officielles plutôt que le scraping quand c'est possible.
    """
    
    BASE_URL = "https://data.rennesmetropole.fr/api/records/1.0/search/"
    
    def get_events(self):
        """Récupère les événements via l'API Open Data."""
        params = {
            "dataset": "agenda-culturel-rennes-metropole", # Nom du dataset trouvé lors de la recherche
            "rows": 10,
            "sort": "date_debut"
        }
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return [
                {
                    "title": r.get("fields", {}).get("titre", "Sans titre"),
                    "date": r.get("fields", {}).get("date_debut", "Inconnue"),
                    "source": "Rennes Open Data"
                }
                for r in data.get("records", [])
            ]
        except Exception as e:
            print(f"Erreur API Rennes Événements: {e}")
            return []

    def get_construction(self):
        """Récupère les travaux en cours via l'API Geotravaux."""
        params = {
            "dataset": "geotravaux",
            "rows": 10
        }
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return [
                {
                    "location": r.get("fields", {}).get("nom_rue", "Lieu inconnu"),
                    "impact": r.get("fields", {}).get("nature", "Travaux"),
                    "source": "Geotravaux Rennes"
                }
                for r in data.get("records", [])
            ]
        except Exception as e:
            print(f"Erreur API Rennes Travaux: {e}")
            return []

    def get_parking_realtime(self):
        """Récupère l'occupation des parkings en temps réel."""
        params = {
            "dataset": "parking-rennes-metropole-temps-reel",
            "rows": 20
        }
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return [
                {
                    "name": r.get("fields", {}).get("nom", "Parking"),
                    "available": r.get("fields", {}).get("libre", 0),
                    "total": r.get("fields", {}).get("total", 0),
                    "source": "Rennes Parking Realtime"
                }
                for r in data.get("records", [])
            ]
        except Exception as e:
            print(f"Erreur API Rennes Parking: {e}")
            return []
