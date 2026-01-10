"""
Utilitaires pour le logging sécurisé
Masque les informations sensibles dans les logs
"""
import re


def mask_email(email: str) -> str:
    """
    Masque un email pour la sécurité dans les logs.
    Exemple: user@example.com -> u***@e***.com
    """
    if not email or '@' not in email:
        return email or ""
    
    try:
        local_part, domain = email.split('@', 1)
        
        # Masquer le local_part (garder le premier caractère)
        if len(local_part) > 1:
            masked_local = local_part[0] + '*' * (len(local_part) - 1)
        else:
            masked_local = local_part
        
        # Masquer le domaine (garder le premier caractère et l'extension)
        if '.' in domain:
            domain_parts = domain.split('.')
            if len(domain_parts) >= 2:
                # Masquer le nom de domaine mais garder l'extension
                domain_name = domain_parts[0]
                extension = '.'.join(domain_parts[1:])
                
                if len(domain_name) > 1:
                    masked_domain = domain_name[0] + '*' * (len(domain_name) - 1) + '.' + extension
                else:
                    masked_domain = domain_name + '.' + extension
            else:
                masked_domain = domain[0] + '*' * (len(domain) - 1) if len(domain) > 1 else domain
        else:
            masked_domain = domain[0] + '*' * (len(domain) - 1) if len(domain) > 1 else domain
        
        return f"{masked_local}@{masked_domain}"
    except Exception:
        # En cas d'erreur, retourner un masque simple
        return "***@***.***"


def mask_phone(phone: str) -> str:
    """
    Masque un numéro de téléphone pour la sécurité dans les logs.
    Exemple: +33123456789 -> +33***56789
    """
    if not phone:
        return ""
    
    # Garder les 3 premiers et 3 derniers caractères
    if len(phone) > 6:
        return phone[:3] + '*' * (len(phone) - 6) + phone[-3:]
    else:
        return '*' * len(phone)


def mask_username(username: str) -> str:
    """
    Masque un nom d'utilisateur pour la sécurité dans les logs.
    Exemple: john_doe -> j***_d***
    """
    if not username:
        return ""
    
    if len(username) <= 2:
        return '*' * len(username)
    
    # Garder le premier et dernier caractère
    return username[0] + '*' * (len(username) - 2) + username[-1]









