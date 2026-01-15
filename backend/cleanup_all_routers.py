#!/usr/bin/env python3
"""
Script pour supprimer l'authentification de tous les routeurs restants
"""
import re
from pathlib import Path

ROUTERS_DIR = Path("backend/app/routers")

def clean_router(file_path: Path):
    """Nettoie un routeur"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # 1. Supprimer import permissions
        content = re.sub(
            r'from app\.utils\.permissions import .*\n',
            '# Authentification supprimée - toutes les routes sont publiques\n',
            content
        )
        
        # 2. Supprimer Depends(get_current_user) et Depends(require_admin)
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
            r'current_user:\s*dict\s*=\s*Depends\(get_current_user\)\s*\n',
            '',
            content
        )
        content = re.sub(
            r'admin_user:\s*dict\s*=\s*Depends\(require_admin\)\s*\n',
            '',
            content
        )
        
        # 3. Remplacer current_user["id"] et current_user.get("id")
        content = re.sub(
            r'current_user\["id"\]',
            '"anonymous"  # Auth supprimée',
            content
        )
        content = re.sub(
            r'current_user\.get\("id"\)',
            '"anonymous"  # Auth supprimée',
            content
        )
        
        # 4. Supprimer vérifications auth
        content = re.sub(
            r'if\s+not\s+current_user.*?raise HTTPException.*?\)',
            '',
            content,
            flags=re.DOTALL
        )
        
        # 5. Mettre à jour docstrings
        content = re.sub(r'\(admin seulement\)', '(route publique)', content)
        content = re.sub(r'\(admin uniquement\)', '(route publique)', content)
        
        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"OK: {file_path.name}")
            return True
        return False
    except Exception as e:
        print(f"ERROR {file_path.name}: {e}")
        return False

# Routeurs à traiter
files = [
    "openai_content.py", "user_history.py", "resources.py",
    "gamification.py", "virtual_labs.py", "avatar.py",
    "exercise_generator.py", "analytics.py", "collaboration.py",
    "anti_cheat.py", "error_learning.py", "prompt_router.py",
    "subscriptions.py", "gdpr.py", "pathways.py",
    "badges.py", "favorites.py", "validation.py",
    "recommendations.py"
]

count = 0
for fname in files:
    fpath = ROUTERS_DIR / fname
    if fpath.exists():
        if clean_router(fpath):
            count += 1
    else:
        print(f"SKIP: {fname} (n'existe pas)")

print(f"\n{count} fichiers modifies")
