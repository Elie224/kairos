"""
Script pour vérifier la configuration OpenAI
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH
script_dir = Path(__file__).parent
backend_dir = script_dir.parent
sys.path.insert(0, str(backend_dir))

def check_openai_config():
    """Vérifie la configuration OpenAI"""
    print("=" * 80)
    print("  VERIFICATION DE LA CONFIGURATION OPENAI")
    print("=" * 80)
    print()
    
    # Vérifier le fichier .env
    env_path = backend_dir / ".env"
    print(f"1. Fichier .env: {env_path}")
    if env_path.exists():
        print(f"   [OK] Fichier .env trouve")
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'OPENAI_API_KEY' in content:
                    # Extraire la clé (sans l'afficher complètement)
                    lines = content.split('\n')
                    for line in lines:
                        if line.strip().startswith('OPENAI_API_KEY='):
                            key_value = line.split('=', 1)[1].strip()
                            if key_value:
                                print(f"   [OK] OPENAI_API_KEY trouvee (longueur: {len(key_value)} caracteres)")
                                print(f"   [OK] Premiers caracteres: {key_value[:20]}...")
                            else:
                                print(f"   [ERREUR] OPENAI_API_KEY est vide")
                            break
                    else:
                        print(f"   [ERREUR] OPENAI_API_KEY non trouvee dans .env")
                else:
                    print(f"   [ERREUR] OPENAI_API_KEY non trouvee dans .env")
        except Exception as e:
            print(f"   [ERREUR] Erreur lors de la lecture du .env: {e}")
    else:
        print(f"   [ERREUR] Fichier .env non trouve")
    
    print()
    
    # Vérifier la configuration via settings
    try:
        from app.config import settings
        print("2. Configuration via settings:")
        if settings.openai_api_key:
            print(f"   [OK] openai_api_key configuree (longueur: {len(settings.openai_api_key)} caracteres)")
            print(f"   [OK] Premiers caracteres: {settings.openai_api_key[:20]}...")
        else:
            print(f"   [ERREUR] openai_api_key non configuree")
        
        print(f"   Modèle par défaut: {settings.openai_model}")
        print(f"   GPT-5.2: {settings.gpt_5_2_model}")
        print(f"   GPT-5-mini: {settings.gpt_5_mini_model}")
        print(f"   GPT-5-nano: {settings.gpt_5_nano_model}")
    except Exception as e:
        print(f"   ❌ Erreur lors du chargement de settings: {e}")
    
    print()
    
    # Vérifier l'initialisation du client
    try:
        from app.services.ai_service import client
        print("3. Client OpenAI:")
        if client:
            print(f"   [OK] Client OpenAI initialise avec succes")
            print(f"   Type: {type(client)}")
        else:
            print(f"   [ERREUR] Client OpenAI non initialise")
            print(f"   [ATTENTION] Verifiez que OPENAI_API_KEY est correctement configuree dans .env")
    except Exception as e:
        print(f"   ❌ Erreur lors de la vérification du client: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 80)
    print("  RÉSUMÉ")
    print("=" * 80)
    
    # Résumé
    env_ok = env_path.exists() and 'OPENAI_API_KEY' in (env_path.read_text(encoding='utf-8') if env_path.exists() else '')
    try:
        from app.config import settings
        settings_ok = bool(settings.openai_api_key)
    except:
        settings_ok = False
    
    try:
        from app.services.ai_service import client
        client_ok = client is not None
    except:
        client_ok = False
    
    if env_ok and settings_ok and client_ok:
        print("[OK] Configuration OpenAI complete et fonctionnelle")
        print()
        print("Si la generation ne fonctionne toujours pas, verifiez:")
        print("  1. Que le backend a ete redemarre apres la configuration")
        print("  2. Les logs du backend pour voir les erreurs exactes")
        print("  3. Que les lecons ont du contenu valide")
    else:
        print("[ERREUR] Configuration OpenAI incomplete")
        if not env_ok:
            print("   - OPENAI_API_KEY manquante dans .env")
        if not settings_ok:
            print("   - openai_api_key non chargee dans settings")
        if not client_ok:
            print("   - Client OpenAI non initialise")
        print()
        print("Actions a effectuer:")
        print("  1. Verifiez que OPENAI_API_KEY est dans .env")
        print("  2. Redemarrez le backend")
        print("  3. Relancez ce script pour verifier")
    
    print("=" * 80)

if __name__ == "__main__":
    check_openai_config()
