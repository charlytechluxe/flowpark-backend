import random
from datetime import datetime

class HabitsEngine:
    """
    Algorithme statistique pour prédire la difficulté de stationnement.
    Basé sur le jour de la semaine, l'heure et des constantes locales.
    """
    
    @staticmethod
    def calculate_difficulty(city: str, timestamp: datetime = None) -> float:
        """
        Calcule un score de difficulté de 0.0 (facile) à 1.0 (très difficile).
        """
        if timestamp is None:
            timestamp = datetime.now()
            
        hour = timestamp.hour
        day = timestamp.weekday()  # 0=Lundi, 6=Dimanche
        
        # Base de difficulté (plus élevé pour Rennes car plus grande ville)
        base_score = 0.4 if city.lower() == "rennes" else 0.2
        
        # Facteur Heure de pointe (8h-9h et 17h-19h)
        rush_hour_factor = 0.0
        if (8 <= hour <= 9) or (17 <= hour <= 19):
            rush_hour_factor = 0.4
        elif (11 <= hour <= 14): # Déjeuner
            rush_hour_factor = 0.2
            
        # Facteur Weekend
        weekend_factor = 0.1 if day >= 5 else 0.0
        
        # Simulation d'événements aléatoires (micro-fluctuations)
        random_noise = random.uniform(-0.05, 0.05)
        
        score = base_score + rush_hour_factor + weekend_factor + random_noise
        return max(0.0, min(1.0, score))

    @staticmethod
    def get_prediction_summary(city: str) -> str:
        score = HabitsEngine.calculate_difficulty(city)
        if score < 0.3:
            return "Stationnement facile"
        elif score < 0.6:
            return "Stationnement modéré"
        else:
            return "Stationnement difficile - Anticipez !"
