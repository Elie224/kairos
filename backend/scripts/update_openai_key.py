"""
Script pour mettre à jour la clé API OpenAI dans le fichier .env
"""
import os
import re
from pathlib import Path

# Nouvelle clé API (doit être fournie via variable d'environnement ou argument)
# NE JAMAIS hardcoder la clé API dans le code source !
NEW_API_KEY = os.getenv("OPENAI_API_KEY") or input("Entrez votre clé API OpenAI: ").strip()

if not NEW_API_KEY:
    print("[ERREUR] Clé API OpenAI requise !")
    print("[INFO] Fournissez-la via variable d'environnement OPENAI_API_KEY ou entrez-la manuellement")
    exit(1)

def update_env_file():
    """Met à jour le fichier .env avec la nouvelle clé API"""
    script_dir = Path(__file__).parent
    backend_dir = script_dir.parent
    env_file = backend_dir / ".env"
    
    if not env_file.exists():
        print(f"[INFO] Fichier .env non trouve a {env_file}")
        print(f"[INFO] Creation du fichier .env...")
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(f"OPENAI_API_KEY={NEW_API_KEY}\n")
        print(f"[OK] Fichier .env cree avec la cle API")
        return
    
    # Lire le contenu actuel
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier si OPENAI_API_KEY existe déjà
    if re.search(r'^OPENAI_API_KEY\s*=', content, re.MULTILINE):
        # Remplacer la clé existante
        new_content = re.sub(
            r'^OPENAI_API_KEY\s*=.*$',
            f'OPENAI_API_KEY={NEW_API_KEY}',
            content,
            flags=re.MULTILINE
        )
        print("[OK] Cle API OpenAI mise a jour dans .env")
    else:
        # Ajouter la clé à la fin du fichier
        new_content = content
        if not new_content.endswith('\n'):
            new_content += '\n'
        new_content += f'OPENAI_API_KEY={NEW_API_KEY}\n'
        print("[OK] Cle API OpenAI ajoutee dans .env")
    
    # Écrire le nouveau contenu
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

if __name__ == "__main__":
    print("=" * 80)
    print("  MISE A JOUR DE LA CLE API OPENAI")
    print("=" * 80)
    print("")
    update_env_file()
    print("")
    print("[OK] Configuration terminee")
    print("")
    print("[IMPORTANT] Redemarrez le backend pour que les changements prennent effet")
    print("=" * 80)
