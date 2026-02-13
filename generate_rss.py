import requests
from feedgen.feed import FeedGenerator
from datetime import datetime
import os

# URL de secours si l'API data.gouv fait des siennes
DATA_URL = "https://www.data.gouv.fr/api/1/datasets/r/c94c9dfe-23eb-45aa-acd1-7438c4e977db"

def create_feed():
    fg = FeedGenerator()
    fg.title('Pétitions - Assemblée Nationale')
    fg.link(href='https://petitions.assemblee-nationale.fr', rel='alternate')
    fg.description('Flux mis à jour via GitHub Actions')
    fg.language('fr')

    # On ajoute un User-Agent pour éviter d'être bloqué
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        print(f"Tentative de récupération des données depuis {DATA_URL}...")
        response = requests.get(DATA_URL, headers=headers, timeout=30)
        
        # Affiche le début de la réponse pour déboguer dans GitHub Actions
        print(f"Statut de la réponse : {response.status_code}")
        
        response.raise_for_status()
        
        petitions = response.json()
        print(f"{len(petitions)} pétitions trouvées.")
        
        for p in petitions:
            if not isinstance(p, dict): continue
            fe = fg.add_entry()
            p_id = str(p.get('id'))
            nb_signatures = p.get('nb_votes', 0)
            titre = p.get('titre', 'Sans titre')
            
            fe.title(f"[{nb_signatures} signatures] {titre}")
            fe.link(href=f"https://petitions.assemblee-nationale.fr/initiatives/{p_id}")
            fe.id(p_id)
            
            resume = p.get('resume') or p.get('description') or ""
            fe.description(f"<b>Signatures : {nb_signatures}</b><br><br>{resume}")

        if not os.path.exists('public'):
            os.makedirs('public')
            
        fg.rss_file('public/rss.xml')
        print("Fichier rss.xml généré avec succès.")

    except Exception as e:
        print(f"Erreur lors de la lecture du JSON : {e}")
        # Optionnel : afficher le contenu de la réponse pour comprendre l'erreur
        if 'response' in locals():
            print(f"Contenu reçu : {response.text[:200]}...")
        raise e # On fait échouer le job pour être prévenu

if __name__ == "__main__":
    create_feed()
