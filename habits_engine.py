import random
from datetime import datetime

class HabitsEngine:
    """
    Algorithme 1.1 : Prédiction intelligente avec météo et événements.
    """
    
    @staticmethod
    def calculate_difficulty(city: str, weather_impact: bool = False, event_count: int = 0) -> float:
        """
        Calcule un score de difficulté de 0.0 à 1.0.
        Pondéré par l'heure, la météo (+15%) et les événements réels (+20%).
        """
        timestamp = datetime.now()
        hour = timestamp.hour
        day = timestamp.weekday()
        
        # Base (Ville)
        score = 0.4 if city.lower() == "rennes" else 0.2
        
        # 1. Facteur Temporel (Heures de pointe)
        if (8 <= hour <= 9) or (17 <= hour <= 19):
            score += 0.4
        elif (11 <= hour <= 14):
            score += 0.2
            
        # 2. Facteur Dynamic : Événements réels (+20% par tranche d'événements)
        if event_count > 0:
            score += 0.20
            
        # 3. Facteur Météo (+15% si pluie/mauvais temps)
        if weather_impact:
            score += 0.15
            
        # 4. Facteur Weekend
        if day >= 5:
            score += 0.1
        
        # Bruit aléatoire (réalité imprévisible)
        score += random.uniform(-0.03, 0.03)
        
        return max(0.0, min(1.0, score))

    @staticmethod
    def get_prediction_summary(score: float) -> str:
        if score < 0.35:
            return "Stationnement fluide (Vert)"
        elif score < 0.65:
            return "Stationnement tendu (Orange)"
        else:
            return "Secteur saturé (Rouge)"
