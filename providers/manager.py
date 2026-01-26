from typing import Dict, Type
from .base import CityProvider
from .laval import LavalProvider
from .rennes import RennesProvider

class CityManager:
    """
    Gère l'enregistrement et l'accès aux fournisseurs de villes.
    Pour ajouter une ville : créer un provider et l'ajouter au dictionnaire REGISTRY.
    """
    
    REGISTRY: Dict[str, Type[CityProvider]] = {
        "laval": LavalProvider,
        "rennes": RennesProvider
    }

    @classmethod
    def get_provider(cls, city: str) -> CityProvider:
        provider_class = cls.REGISTRY.get(city.lower())
        if not provider_class:
            raise ValueError(f"La ville '{city}' n'est pas supportée.")
        return provider_class()

    @classmethod
    def get_supported_cities(cls):
        return list(cls.REGISTRY.keys())
