import requests
from feedgen.feed import FeedGenerator
from datetime import datetime
import os

# Ton lien direct data.gouv.fr
DATA_URL = "https://www.data.gouv.fr/api/1/datasets/r/c94c9dfe-23eb-45aa-acd1-7438c4e977db"

def create_feed():
    fg = FeedGenerator()
    fg.title('Pétitions - Assemblée Nationale (Data.gouv)')
    fg.link(href='https://petitions.assemblee-nationale.fr', rel='alternate')
    fg.description('Suivi des signatures via l\'API Data.gouv.fr')
    fg.language('fr')

    try:
        response = requests.get(DATA_URL, timeout=30)
        response.raise_for_status()
        # Le fichier JSON de ton lien est une liste directe d'objets
        petitions = response.json()
        
        for p in petitions:
            # On vérifie si c'est bien un dictionnaire (sécurité)
            if not isinstance(p, dict): continue

            fe = fg.add_entry()
            
            # Utilisation de 'nb_votes' comme tu l'as sagement remarqué
            p_id = str(p.get('id'))
            nb_signatures = p.get('nb_votes', 0)
            titre = p.get('titre', 'Sans titre')
            
            # Titre optimisé pour Miniflux
            fe.title(f"[{nb_signatures} sig.] {titre}")
            
            # URL de la pétition
            url = f"https://petitions.assemblee-nationale.fr/initiatives/{p_id}"
            fe.link(href=url)
            fe.id(p_id)

            # Description (Vérification des champs présents dans l'export)
            # Note : Certains champs comme 'resume' peuvent être nommés 'description' ou 'texte'
            resume = p.get('resume') or p.get('description') or "Pas de description."
            statut = p.get('statut_label') or p.get('statut') or "N/A"
            
            content = f"""
            <p><strong>Signatures :</strong> {nb_signatures}</p>
            <p><strong>Statut :</strong> {statut}</p>
            <hr>
            {resume}
            """
            fe.description(content)

            # Date : le champ est souvent 'date_creation' dans l'export CSV/JSON
            date_str = p.get('date_creation') or p.get('date_depot')
            if date_str:
                try:
                    # Gestion du format possible '2023-10-25' ou ISO
                    if len(date_str) == 10:
                        dt = datetime.strptime(date_str, '%Y-%m-%d')
                    else:
                        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    fe.pubDate(dt)
                except:
                    pass

        if not os.path.exists('public'):
            os.makedirs('public')
            
        fg.rss_file('public/rss.xml')
        print(f"Flux RSS généré : {len(petitions)} items.")

    except Exception as e:
        print(f"Erreur lors de la lecture du JSON : {e}")

if __name__ == "__main__":
    create_feed()
