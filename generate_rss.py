import requests
import csv
import io
from feedgen.feed import FeedGenerator
from datetime import datetime
import pytz # Pour la gestion propre des fuseaux horaires
import os

DATA_URL = "https://www.data.gouv.fr/api/1/datasets/r/c94c9dfe-23eb-45aa-acd1-7438c4e977db"

def create_feed():
    fg = FeedGenerator()
    fg.title('Pétitions - Assemblée Nationale')
    fg.link(href='https://petitions.assemblee-nationale.fr', rel='alternate')
    fg.description('Flux mis à jour depuis l\'export CSV de data.gouv.fr')
    fg.language('fr')

    # Fuseau horaire de Paris
    paris_tz = pytz.timezone('Europe/Paris')

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(DATA_URL, headers=headers, timeout=30)
        response.raise_for_status()
        
        content = response.content.decode('utf-8')
        f = io.StringIO(content)
        reader = csv.DictReader(f, delimiter=';')
        
        for row in reader:
            fe = fg.add_entry()
            
            titre = row.get('titre', 'Sans titre')
            nb_signatures = row.get('nb_votes', '0')
            description = row.get('description', '')
            p_url = row.get('url', 'https://petitions.assemblee-nationale.fr')
            p_id = row.get('identifiant') or p_url.split('/')[-1]
            
            fe.title(f"[{nb_signatures} signatures] {titre}")
            fe.link(href=p_url)
            fe.id(p_id)
            fe.description(f"<b>Signatures : {nb_signatures}</b><br><br>{description}")

            # CORRECTION DE LA DATE
            date_str = row.get('date_publication')
            if date_str:
                try:
                    # On convertit '2023-10-25' en objet datetime à midi pour éviter les bugs de fuseau
                    dt = datetime.strptime(date_str[:10], '%Y-%m-%d')
                    # On localise la date avec le fuseau de Paris
                    dt_aware = paris_tz.localize(dt.replace(hour=12, minute=0))
                    fe.pubDate(dt_aware)
                except Exception as e:
                    print(f"Erreur date sur {p_id}: {e}")
            
        if not os.path.exists('public'):
            os.makedirs('public')
            
        fg.rss_file('public/rss.xml')
        print("Flux RSS généré avec dates corrigées.")

    except Exception as e:
        print(f"Erreur : {e}")
        raise e

if __name__ == "__main__":
    create_feed()
