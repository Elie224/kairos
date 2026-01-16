"""
Utilitaires de sécurité
"""
import re
import hashlib
import secrets
from typing import Optional
from passlib.context import CryptContext
from pydantic import EmailStr
from fastapi import HTTPException, status
import logging
import bcrypt

logger = logging.getLogger(__name__)

# Configuration du contexte de hachage de mot de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordValidator:
    """Validateur de mot de passe avec règles de sécurité"""
    
    MIN_LENGTH = 8
    MAX_LENGTH = 128
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL = True
    
    # Caractères spéciaux autorisés
    SPECIAL_CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    # Mots de passe communs à éviter
    COMMON_PASSWORDS = {
        "password", "12345678", "qwerty", "abc123", "password123",
        "admin", "letmein", "welcome", "monkey", "1234567890",
        "password1", "qwerty123", "admin123", "root", "toor"
    }
    
    @classmethod
    def validate(cls, password: str) -> tuple[bool, Optional[str]]:
        """
        Valide un mot de passe selon les règles de sécurité
        
        Returns:
            tuple: (is_valid, error_message)
        """
        if not password:
            return False, "Le mot de passe est requis"
        
        # Vérifier la longueur
        if len(password) < cls.MIN_LENGTH:
            return False, f"Le mot de passe doit contenir au moins {cls.MIN_LENGTH} caractères"
        
        if len(password) > cls.MAX_LENGTH:
            return False, f"Le mot de passe ne doit pas dépasser {cls.MAX_LENGTH} caractères"
        
        # Vérifier les caractères requis
        if cls.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            return False, "Le mot de passe doit contenir au moins une majuscule"
        
        if cls.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            return False, "Le mot de passe doit contenir au moins une minuscule"
        
        if cls.REQUIRE_DIGIT and not re.search(r'\d', password):
            return False, "Le mot de passe doit contenir au moins un chiffre"
        
        if cls.REQUIRE_SPECIAL and not re.search(f'[{re.escape(cls.SPECIAL_CHARS)}]', password):
            return False, f"Le mot de passe doit contenir au moins un caractère spécial ({cls.SPECIAL_CHARS})"
        
        # Vérifier les mots de passe communs
        if password.lower() in cls.COMMON_PASSWORDS:
            return False, "Ce mot de passe est trop commun. Veuillez en choisir un autre."
        
        # Vérifier les séquences répétitives
        if re.search(r'(.)\1{3,}', password):
            return False, "Le mot de passe ne doit pas contenir de séquences répétitives"
        
        # Vérifier les séquences de clavier (ex: qwerty, 12345)
        keyboard_sequences = [
            "qwerty", "asdf", "zxcv", "12345", "abcde", "qwertyuiop"
        ]
        password_lower = password.lower()
        for seq in keyboard_sequences:
            if seq in password_lower or seq[::-1] in password_lower:
                return False, "Le mot de passe ne doit pas contenir de séquences de clavier"
        
        return True, None
    
    @classmethod
    def calculate_strength(cls, password: str) -> int:
        """
        Calcule la force du mot de passe (0-100)
        
        Returns:
            int: Score de force (0-100)
        """
        score = 0
        
        # Longueur
        if len(password) >= 8:
            score += 10
        if len(password) >= 12:
            score += 10
        if len(password) >= 16:
            score += 10
        
        # Complexité
        if re.search(r'[a-z]', password):
            score += 10
        if re.search(r'[A-Z]', password):
            score += 10
        if re.search(r'\d', password):
            score += 10
        if re.search(f'[{re.escape(cls.SPECIAL_CHARS)}]', password):
            score += 10
        
        # Diversité des caractères
        unique_chars = len(set(password))
        if unique_chars >= len(password) * 0.7:
            score += 10
        
        # Pénalités
        if password.lower() in cls.COMMON_PASSWORDS:
            score -= 50
        
        return min(max(score, 0), 100)


class InputSanitizer:
    """Sanitiseur d'entrée pour prévenir les injections"""
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """Nettoie une chaîne de caractères"""
        if not value:
            return ""
        
        # Limiter la longueur
        value = value[:max_length]
        
        # Supprimer les caractères de contrôle
        value = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)
        
        # Normaliser les espaces
        value = re.sub(r'\s+', ' ', value).strip()
        
        return value
    
    @staticmethod
    def sanitize_email(email: str) -> Optional[str]:
        """Valide et nettoie un email"""
        if not email:
            return None
        
        try:
            # Nettoyer l'email
            email_cleaned = email.lower().strip()
            
            # Validation avec regex (format standard)
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, email_cleaned):
                logger.warning(f"Email ne correspond pas au format regex: {email_cleaned}")
                return None
            
            # Validation Pydantic (EmailStr utilise email-validator en arrière-plan)
            # On utilise validate_email de pydantic pour valider
            from pydantic import validate_email
            validation_result = validate_email(email_cleaned)
            # validate_email retourne un tuple (local_part, normalized_email)
            if isinstance(validation_result, tuple) and len(validation_result) >= 2:
                return validation_result[1]  # Retourner l'email normalisé
            return str(validation_result)
        except Exception as e:
            logger.warning(f"Erreur lors de la validation de l'email '{email}': {e}")
            # En cas d'erreur avec Pydantic, utiliser la validation regex uniquement
            email_cleaned = email.lower().strip()
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if re.match(email_regex, email_cleaned):
                return email_cleaned
            return None
    
    @staticmethod
    def sanitize_object_id(value: str) -> Optional[str]:
        """Valide un ObjectId MongoDB"""
        from bson import ObjectId
        
        if not value:
            return None
        
        # Vérifier le format (24 caractères hexadécimaux)
        if not re.match(r'^[0-9a-fA-F]{24}$', value):
            return None
        
        try:
            # Vérifier que c'est un ObjectId valide
            ObjectId(value)
            return value
        except Exception:
            return None
    
    @staticmethod
    def prevent_nosql_injection(query: dict) -> dict:
        """Prévient les injections NoSQL en nettoyant les requêtes"""
        sanitized = {}
        
        for key, value in query.items():
            # Supprimer les opérateurs MongoDB dangereux
            if key.startswith("$"):
                continue
            
            # Nettoyer les valeurs
            if isinstance(value, str):
                sanitized[key] = InputSanitizer.sanitize_string(value)
            elif isinstance(value, dict):
                # Récursivement nettoyer les dictionnaires
                sanitized[key] = InputSanitizer.prevent_nosql_injection(value)
            else:
                sanitized[key] = value
        
        return sanitized


class PasswordHasher:
    """Gestionnaire de hachage de mots de passe"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hache un mot de passe"""
        # Bcrypt a une limite stricte de 72 bytes
        # Pour garantir la compatibilité, on pré-hash TOUJOURS avec SHA256
        password_bytes = password.encode('utf-8')
        password_length = len(password_bytes)
        
        # Pré-hash avec SHA256 (32 bytes)
        sha256_hash_bytes = hashlib.sha256(password_bytes).digest()
        
        # Convertir en hexadécimal (64 caractères = 64 bytes, bien sous la limite de 72)
        sha256_hash_hex = sha256_hash_bytes.hex()
        
        logger.debug(f"Mot de passe de {password_length} bytes, pré-hash SHA256 (hex): {sha256_hash_hex[:16]}...")
        
        try:
            # Utiliser directement bcrypt au lieu de passlib pour éviter les problèmes de détection de bug
            # Le hash hex fait 64 bytes, bien sous la limite de 72 bytes
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(sha256_hash_hex.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"Erreur lors du hachage avec bcrypt: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors du hachage du mot de passe: {str(e)}"
            )
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Vérifie un mot de passe"""
        try:
            logger.debug(f"Vérification du mot de passe (longueur: {len(plain_password)}), hash (premiers 20 chars): {hashed_password[:20]}...")
            password_bytes = plain_password.encode('utf-8')
            
            # Pré-hash avec SHA256 en hex (même logique que hash_password)
            sha256_hash_bytes = hashlib.sha256(password_bytes).digest()
            sha256_hash_hex = sha256_hash_bytes.hex()
            logger.debug(f"Pré-hash SHA256 (premiers 16 chars): {sha256_hash_hex[:16]}...")
            
            # Essayer d'abord avec le pré-hash SHA256 hex (nouvelle méthode avec bcrypt direct)
            try:
                result = bcrypt.checkpw(sha256_hash_hex.encode('utf-8'), hashed_password.encode('utf-8'))
                logger.debug(f"Résultat de bcrypt.checkpw avec pré-hash SHA256: {result}")
                if result:
                    return True
            except Exception as e:
                logger.warning(f"Erreur lors de la vérification avec pré-hash SHA256: {e}")
                pass
            
            # Essayer avec le mot de passe direct (compatibilité avec anciens mots de passe via passlib)
            try:
                if pwd_context.verify(plain_password, hashed_password):
                    return True
            except:
                pass
            
            # Essayer aussi avec base64 pour compatibilité avec anciens hashs
            import base64
            sha256_hash_base64 = base64.b64encode(sha256_hash_bytes).decode('utf-8')
            try:
                if pwd_context.verify(sha256_hash_base64, hashed_password):
                    return True
            except:
                pass
            
            # Essayer aussi avec hex via passlib (compatibilité)
            try:
                if pwd_context.verify(sha256_hash_hex, hashed_password):
                    return True
            except:
                pass
            
            return False
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du mot de passe: {e}")
            return False
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Génère un token sécurisé"""
        return secrets.token_urlsafe(length)


class CSRFProtection:
    """Protection CSRF basique"""
    
    @staticmethod
    def generate_csrf_token() -> str:
        """Génère un token CSRF"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def verify_csrf_token(token: str, stored_token: str) -> bool:
        """Vérifie un token CSRF"""
        return secrets.compare_digest(token, stored_token)

