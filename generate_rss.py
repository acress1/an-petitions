import requests
import csv
import io
from feedgen.feed import FeedGenerator
from datetime import datetime
import pytz
import os

DATA_URL = "https://www.data.gouv.fr/api/1/datasets/r/c94c9dfe-23eb-45aa-acd1-7438c4e977db"

def create_feed():
    fg = FeedGenerator()
    fg.title('Pétitions - Assemblée Nationale')
    fg.link(href='https://petitions.assemblee-nationale.fr', rel='alternate')
    fg.description('Suivi des signatures via data.gouv.fr')
    fg.language('fr')

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
        
        items_count = 0
        for row in reader:
            fe = fg.add_entry()
            
            titre = row.get('titre', 'Sans titre')
            nb_signatures = row.get('nb_votes', '0')
            p_url = row.get('url', 'https://petitions.assemblee-nationale.fr')
            p_id = row.get('identifiant') or p_url.split('/')[-1]
            
            fe.title(f"[{nb_signatures} sig.] {titre}")
            fe.link(href=p_url)
            fe.id(p_id)
            fe.description(f"<b>Signatures : {nb_signatures}</b><br><br>{row.get('description', '')}")

            # GESTION RIGOUREUSE DE LA DATE
            # On cherche 'date_publication' ou 'date_creation' selon l'export
            date_raw = row.get('date_publication') or row.get('date_creation')
            
            if date_raw:
                try:
                    # Nettoyage de la chaîne (on prend les 10 premiers caractères : YYYY-MM-DD)
                    clean_date = date_raw.strip()[:10]
                    dt = datetime.strptime(clean_date, '%Y-%m-%d')
                    # On ajoute l'heure et le fuseau horaire
                    dt_aware = paris_tz.localize(dt.replace(hour=12, minute=0))
                    fe.pubDate(dt_aware)
                except Exception as e:
                    print(f"Format de date inconnu pour {p_id} : {date_raw}")
            
            items_count += 1

        if not os.path.exists('public'):
            os.makedirs('public')
            
        fg.rss_file('public/rss.xml')
        print(f"Succès : {items_count} items générés dans rss.xml")

    except Exception as e:
        print(f"Erreur fatale : {e}")
        raise e

if __name__ == "__main__":
    create_feed()
