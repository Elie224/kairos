"""
Routeur pour le support et les messages de contact
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.database import get_database
from app.schemas import serialize_doc
from app.utils.permissions import require_admin
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class SupportMessage(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    subject: str
    message: str
    supportType: str = "general"  # general, financial, technical, partnership


class SupportMessageResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    subject: str
    message: str
    support_type: str
    created_at: datetime
    read: bool
    responded: bool
    
    class Config:
        from_attributes = True


@router.post("/contact", status_code=status.HTTP_201_CREATED)
async def create_support_message(message: SupportMessage):
    """Crée un nouveau message de soutien"""
    try:
        db = get_database()
        
        # Préparer le document à insérer
        message_doc = {
            "name": message.name.strip(),
            "email": message.email.lower().strip(),
            "phone": message.phone.strip() if message.phone else None,
            "subject": message.subject.strip(),
            "message": message.message.strip(),
            "support_type": message.supportType,
            "created_at": datetime.utcnow(),
            "read": False,
            "responded": False,
        }
        
        # Insérer dans la collection support_messages
        result = await db.support_messages.insert_one(message_doc)
        message_doc["_id"] = result.inserted_id
        
        logger.info(f"Nouveau message de soutien reçu de {message.email} - Type: {message.supportType}")
        
        return {
            "message": "Votre message a été envoyé avec succès. Nous vous contacterons bientôt.",
            "id": str(result.inserted_id)
        }
    except Exception as e:
        logger.error(f"Erreur lors de la création du message de soutien: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'envoi du message. Veuillez réessayer."
        )


@router.get("/messages", response_model=List[SupportMessageResponse])
async def get_support_messages(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    unread_only: bool = Query(False),
    admin_user: dict = Depends(require_admin)
):
    """Récupère tous les messages de support (admin seulement)"""
    try:
        db = get_database()
        
        # Construire le filtre
        filter_query = {}
        if unread_only:
            filter_query["read"] = False
        
        # Récupérer les messages triés par date (plus récents en premier)
        cursor = db.support_messages.find(filter_query).sort("created_at", -1).skip(skip).limit(limit)
        messages = await cursor.to_list(length=limit)
        
        # Sérialiser les messages
        result = []
        for msg in messages:
            serialized = serialize_doc(msg)
            result.append(serialized)
        
        return result
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des messages de support: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des messages"
        )


@router.put("/messages/{message_id}/read")
async def mark_message_as_read(
    message_id: str,
    admin_user: dict = Depends(require_admin)
):
    """Marque un message comme lu (admin seulement)"""
    try:
        from bson import ObjectId
        
        db = get_database()
        
        # Vérifier que l'ID est valide
        try:
            obj_id = ObjectId(message_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de message invalide"
            )
        
        # Mettre à jour le message
        result = await db.support_messages.update_one(
            {"_id": obj_id},
            {"$set": {"read": True}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message non trouvé"
            )
        
        return {"message": "Message marqué comme lu"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la mise à jour du message"
        )


@router.put("/messages/{message_id}/responded")
async def mark_message_as_responded(
    message_id: str,
    admin_user: dict = Depends(require_admin)
):
    """Marque un message comme ayant reçu une réponse (admin seulement)"""
    try:
        from bson import ObjectId
        
        db = get_database()
        
        # Vérifier que l'ID est valide
        try:
            obj_id = ObjectId(message_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de message invalide"
            )
        
        # Mettre à jour le message
        result = await db.support_messages.update_one(
            {"_id": obj_id},
            {"$set": {"responded": True, "read": True}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message non trouvé"
            )
        
        return {"message": "Message marqué comme ayant reçu une réponse"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la mise à jour du message"
        )

















