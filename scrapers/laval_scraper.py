import requests
from bs4 import BeautifulSoup
from datetime import datetime

class LavalScraper:
    """
    Scraper pour récupérer les événements et travaux à Laval.
    Respecte les principes de scraping éthique.
    """
    
    BASE_URL_TOURISM = "https://www.laval-tourisme.com/agenda/"
    BASE_URL_VILLE = "https://www.laval.fr/travaux-et-circulation"
    
    def scrape_events(self):
        """Récupère les événements culturels et touristiques de Laval."""
        events = []
        try:
            # Note: En production, on ajouterait un User-Agent et des délais (time.sleep)
            response = requests.get(self.BASE_URL_TOURISM, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Exemple de sélecteur (basé sur la structure typique d'un site de tourisme)
            # On cherche les articles ou divs contenant les événements
            event_items = soup.find_all('article', class_='item-agenda') # Sélecteur hypothétique
            
            for item in event_items[:10]: # Limite à 10 pour l'exemple
                title = item.find('h2').text.strip() if item.find('h2') else "Événement sans titre"
                date_str = item.find('time').text.strip() if item.find('time') else "Date inconnue"
                
                events.append({
                    "title": title,
                    "date": date_str,
                    "source": "Laval Tourisme"
                })
        except Exception as e:
            print(f"Erreur lors du scraping des événements de Laval: {e}")
            # Fallback avec des données factices si le site change de structure
            events = [
                {"title": "Marché Local", "date": "Samedi matin", "source": "Fallback"},
                {"title": "Concert au Théâtre", "date": "Vendredi soir", "source": "Fallback"}
            ]
            
        return events

    def scrape_construction(self):
        """Récupère les zones de travaux à Laval."""
        construction = []
        try:
            response = requests.get(self.BASE_URL_VILLE, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Recherche des infos travaux sur la page
            work_sections = soup.find_all('div', class_='travaux-item') # Sélecteur hypothétique
            
            for section in work_sections:
                location = section.find('h3').text.strip() if section.find('h3') else "Lieu inconnu"
                description = section.find('p').text.strip() if section.find('p') else "Pas de description"
                
                construction.append({
                    "location": location,
                    "impact": description,
                    "source": "Mairie de Laval"
                })
        except Exception as e:
            print(f"Erreur lors du scraping des travaux de Laval: {e}")
            construction = [
                {"location": "Centre-ville", "impact": "Circulation alternée", "source": "Fallback"}
            ]
            
        return construction
