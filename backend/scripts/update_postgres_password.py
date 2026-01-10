"""
Script pour mettre à jour le mot de passe PostgreSQL dans .env
"""
import os
import re

def update_postgres_password(new_password: str):
    """Met à jour le mot de passe PostgreSQL dans .env"""
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    
    if not os.path.exists(env_file):
        print(f"ERREUR: Fichier .env introuvable: {env_file}")
        return False
    
    # Lire le contenu du fichier
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remplacer ou ajouter POSTGRES_PASSWORD
    pattern = r'^POSTGRES_PASSWORD=.*$'
    replacement = f'POSTGRES_PASSWORD={new_password}'
    
    if re.search(pattern, content, re.MULTILINE):
        # Remplacer la ligne existante
        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    else:
        # Ajouter la ligne si elle n'existe pas
        new_content = content + f'\nPOSTGRES_PASSWORD={new_password}\n'
    
    # Écrire le nouveau contenu
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("OK: Mot de passe PostgreSQL mis a jour dans .env")
    print(f"   POSTGRES_PASSWORD={new_password}")
    return True

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        password = sys.argv[1]
    else:
        password = "Kourouma2025@"
        print(f"Utilisation du mot de passe par défaut: {password}")
        print("Pour utiliser un autre mot de passe: python update_postgres_password.py VOTRE_MOT_DE_PASSE")
        print("")
    
    update_postgres_password(password)
