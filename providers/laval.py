import requests
import logging
from bs4 import BeautifulSoup
from .base import CityProvider

logger = logging.getLogger("flowpark.laval")

class LavalProvider(CityProvider):
    BASE_URL_TOURISM = "https://www.laval-tourisme.com/agenda/"
    BASE_URL_VILLE = "https://www.laval.fr/travaux-et-circulation"
    
    def get_events(self):
        logger.info("Scraping events for Laval...")
        events = []
        try:
            response = requests.get(self.BASE_URL_TOURISM, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            event_items = soup.find_all('article', class_='item-agenda')
            
            for item in event_items[:10]:
                title = item.find('h2').text.strip() if item.find('h2') else "Événement"
                events.append({"title": title, "source": "Laval Tourisme"})
        except Exception as e:
            logger.error(f"Failed to scrape Laval events: {e}")
            events = [{"title": "Marché Local", "source": "Fallback"}]
        return events

    def get_construction(self):
        logger.info("Scraping construction for Laval...")
        construction = []
        try:
            response = requests.get(self.BASE_URL_VILLE, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            work_items = soup.find_all('div', class_='travaux-item')
            for item in work_items:
                loc = item.find('h3').text.strip() if item.find('h3') else "Lieu"
                construction.append({"location": loc, "source": "Mairie de Laval"})
        except Exception as e:
            logger.error(f"Failed to scrape Laval construction: {e}")
            construction = [{"location": "Centre-ville", "source": "Fallback"}]
        return construction

    def get_parking(self):
        return None  # Pas d'API temps réel identifiée pour Laval pour le moment
