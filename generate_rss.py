import requests
import csv
import io
from feedgen.feed import FeedGenerator
from datetime import datetime
import os

# L'URL qui renvoie le CSV
DATA_URL = "https://www.data.gouv.fr/api/1/datasets/r/c94c9dfe-23eb-45aa-acd1-7438c4e977db"

def create_feed():
    fg = FeedGenerator()
    fg.title('Pétitions - Assemblée Nationale')
    fg.link(href='https://petitions.assemblee-nationale.fr', rel='alternate')
    fg.description('Flux mis à jour depuis l\'export CSV de data.gouv.fr')
    fg.language('fr')

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        print(f"Récupération du CSV...")
        response = requests.get(DATA_URL, headers=headers, timeout=30)
        response.raise_for_status()
        
        # On décode le contenu en texte pour le lecteur CSV
        content = response.content.decode('utf-8')
        f = io.StringIO(content)
        
        # Le CSV utilise des points-virgules comme délimiteur
        reader = csv.DictReader(f, delimiter=';')
        
        count = 0
        for row in reader:
            fe = fg.add_entry()
            
            # On utilise les noms de colonnes vus dans tes logs
            titre = row.get('titre', 'Sans titre')
            nb_signatures = row.get('nb_votes', '0')
            description = row.get('description', '')
            p_url = row.get('url', 'https://petitions.assemblee-nationale.fr')
            p_id = row.get('identifiant') or p_url.split('/')[-1]
            statut = row.get('statut', 'N/A')
            
            fe.title(f"[{nb_signatures} signatures] {titre}")
            fe.link(href=p_url)
            fe.id(p_id)
            
            content_html = f"<b>Statut : {statut}</b><br><b>Signatures : {nb_signatures}</b><br><br>{description}"
            fe.description(content_html)

            # Gestion de la date (colonne date_publication)
            date_str = row.get('date_publication')
            if date_str:
                try:
                    # On tente le format YYYY-MM-DD
                    dt = datetime.strptime(date_str[:10], '%Y-%m-%d')
                    fe.pubDate(dt.replace(tzinfo=None))
                except:
                    pass
            
            count += 1

        if not os.path.exists('public'):
            os.makedirs('public')
            
        fg.rss_file('public/rss.xml')
        print(f"Succès : {count} pétitions ajoutées au flux RSS.")

    except Exception as e:
        print(f"Erreur : {e}")
        raise e

if __name__ == "__main__":
    create_feed()
