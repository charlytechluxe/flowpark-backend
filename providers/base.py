from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class CityProvider(ABC):
    """
    Interface de base pour les fournisseurs de données urbaines.
    Permet d'ajouter une ville en implémentant simplement ces méthodes.
    """
    
    @abstractmethod
    def get_events(self) -> List[Dict]:
        pass

    @abstractmethod
    def get_construction(self) -> List[Dict]:
        pass

    @abstractmethod
    def get_parking(self) -> Optional[List[Dict]]:
        pass
