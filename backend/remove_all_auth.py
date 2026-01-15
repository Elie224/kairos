#!/usr/bin/env python3
"""
Script pour supprimer automatiquement l'authentification de tous les routeurs backend restants.
"""
import re
from pathlib import Path

ROUTERS_DIR = Path(__file__).parent / "app" / "routers"

def remove_auth_from_file(file_path: Path):
    """Supprime l'authentification d'un fichier routeur"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 1. Supprimer les imports d'authentification
        content = re.sub(
            r'from app\.utils\.permissions import .*\n',
            '# Authentification supprimée - toutes les routes sont publiques\n',
            content
        )
        
        # 2. Supprimer les paramètres Depends(get_current_user) et Depends(require_admin)
        content = re.sub(
            r',\s*current_user:\s*dict\s*=\s*Depends\(get_current_user\)',
            '',
            content
        )
        content = re.sub(
            r',\s*admin_user:\s*dict\s*=\s*Depends\(require_admin\)',
            '',
            content
        )
        content = re.sub(
            r'current_user:\s*dict\s*=\s*Depends\(get_current_user\),?\s*\n',
            '',
            content
        )
        content = re.sub(
            r'admin_user:\s*dict\s*=\s*Depends\(require_admin\),?\s*\n',
            '',
            content
        )
        
        # 3. Remplacer current_user.get("id") et current_user["id"] par "anonymous"
        content = re.sub(
            r'current_user\.get\("id"\)',
            '"anonymous"  # Auth supprimée',
            content
        )
        content = re.sub(
            r'current_user\["id"\]',
            '"anonymous"  # Auth supprimée',
            content
        )
        content = re.sub(
            r'current_user\.get\("is_admin"',
            'False  # Auth supprimée',
            content
        )
        
        # 4. Supprimer les vérifications d'authentification
        content = re.sub(
            r'if\s+not\s+current_user\s+or\s+not\s+current_user\.get\("id"\):.*?raise HTTPException\([^)]+\)',
            '',
            content,
            flags=re.DOTALL
        )
        content = re.sub(
            r'if\s+not\s+user_id:.*?raise HTTPException\([^)]+\)',
            '',
            content,
            flags=re.DOTALL
        )
        
        # 5. Supprimer les vérifications is_admin
        content = re.sub(
            r'if\s+not\s+current_user\.get\("is_admin",\s*False\):.*?raise HTTPException\([^)]+\)',
            '',
            content,
            flags=re.DOTALL
        )
        
        # 6. Supprimer les vérifications d'appartenance
        content = re.sub(
            r'if\s+.*?\.get\("user_id"\)\s+!=\s+current_user\["id"\]:.*?raise HTTPException\([^)]+\)',
            '# Plus de vérification d\'appartenance (auth supprimée)',
            content,
            flags=re.DOTALL
        )
        
        # 7. Mettre à jour les docstrings
        content = re.sub(
            r'\(admin seulement\)|\(admin uniquement\)',
            '(route publique)',
            content
        )
        content = re.sub(
            r'Récupère.*?utilisateur',
            lambda m: m.group(0).replace('utilisateur', '') + ' (route publique)',
            content
        )
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] Modifie: {file_path.name}")
            return True
        else:
            print(f"[SKIP] Aucun changement: {file_path.name}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Erreur avec {file_path.name}: {e}")
        return False

def main():
    """Traite tous les routeurs restants"""
    router_files = list(ROUTERS_DIR.glob("*.py"))
    router_files = [f for f in router_files if f.name != "__init__.py"]
    
    # Exclure les fichiers déjà traités
    already_done = {
        "auth.py",  # Supprimé
        "feedback.py",
        "pedagogical_memory.py",
        "modules.py",
        "ai_tutor.py",
        "progress.py",
        "exam.py",
        "quiz.py",
        "support.py",
        "td.py",
        "tp.py"
    }
    
    router_files = [f for f in router_files if f.name not in already_done]
    
    print(f"Traitement de {len(router_files)} routeurs...\n")
    
    modified_count = 0
    for router_file in sorted(router_files):
        if remove_auth_from_file(router_file):
            modified_count += 1
    
    print(f"\n[OK] {modified_count} fichier(s) modifie(s) sur {len(router_files)}")

if __name__ == "__main__":
    main()
