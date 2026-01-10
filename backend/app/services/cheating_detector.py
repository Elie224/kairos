"""
Service pour détecter la triche et le plagiat avec IA
"""
from typing import Dict, Any, List, Optional
from app.services.ai_service import client, AI_MODEL
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class CheatingDetector:
    """Détecteur de triche et plagiat"""
    
    @staticmethod
    async def detect_plagiarism(
        user_answer: str,
        other_answers: List[str],
        question: str
    ) -> Dict[str, Any]:
        """
        Détecte la similarité avec d'autres réponses (plagiat)
        """
        try:
            if not client or not other_answers:
                return {
                    "similarity_score": 0.0,
                    "is_plagiarized": False,
                    "similar_answers": []
                }
            
            # Calculer similarité avec chaque autre réponse
            similarities = []
            for other_answer in other_answers[:10]:  # Limiter à 10 pour performance
                similarity = await CheatingDetector._calculate_similarity(
                    user_answer,
                    other_answer,
                    question
                )
                similarities.append({
                    "answer": other_answer[:100],  # Tronquer pour réponse
                    "similarity": similarity
                })
            
            # Trouver la similarité maximale
            max_similarity = max(s["similarity"] for s in similarities) if similarities else 0.0
            
            # Seuil de plagiat (ajustable)
            plagiarism_threshold = 0.85
            is_plagiarized = max_similarity >= plagiarism_threshold
            
            return {
                "similarity_score": max_similarity,
                "is_plagiarized": is_plagiarized,
                "similar_answers": [s for s in similarities if s["similarity"] >= plagiarism_threshold],
                "confidence": "high" if max_similarity > 0.9 else "medium" if max_similarity > 0.7 else "low"
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la détection de plagiat: {e}", exc_info=True)
            return {
                "similarity_score": 0.0,
                "is_plagiarized": False,
                "similar_answers": []
            }
    
    @staticmethod
    async def analyze_behavior_anomalies(
        user_id: str,
        answer_times: List[float],
        scores: List[float],
        average_time: float
    ) -> Dict[str, Any]:
        """
        Analyse les anomalies comportementales (temps réponse, scores)
        """
        try:
            anomalies = []
            
            # Détecter temps de réponse anormalement courts
            if answer_times:
                avg_time = sum(answer_times) / len(answer_times)
                if avg_time < average_time * 0.3:  # 70% plus rapide que la moyenne
                    anomalies.append({
                        "type": "suspiciously_fast",
                        "severity": "high",
                        "description": "Temps de réponse anormalement courts"
                    })
            
            # Détecter scores parfaitement constants (possible triche)
            if len(set(scores)) == 1 and len(scores) > 5:
                anomalies.append({
                    "type": "constant_perfect_scores",
                    "severity": "medium",
                    "description": "Scores parfaitement identiques sur plusieurs tentatives"
                })
            
            # Détecter amélioration soudaine et suspecte
            if len(scores) > 3:
                recent_avg = sum(scores[-3:]) / 3
                previous_avg = sum(scores[:-3]) / (len(scores) - 3) if len(scores) > 3 else recent_avg
                if recent_avg > previous_avg + 30:  # Amélioration de 30 points
                    anomalies.append({
                        "type": "sudden_improvement",
                        "severity": "low",
                        "description": "Amélioration soudaine des scores"
                    })
            
            risk_score = sum(
                0.5 if a["severity"] == "high" else 0.3 if a["severity"] == "medium" else 0.1
                for a in anomalies
            )
            
            return {
                "user_id": user_id,
                "anomalies_detected": len(anomalies),
                "anomalies": anomalies,
                "risk_score": min(risk_score, 1.0),
                "requires_review": risk_score > 0.5
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse comportementale: {e}", exc_info=True)
            return {
                "user_id": user_id,
                "anomalies_detected": 0,
                "anomalies": [],
                "risk_score": 0.0,
                "requires_review": False
            }
    
    @staticmethod
    async def _calculate_similarity(
        answer1: str,
        answer2: str,
        question: str
    ) -> float:
        """Calcule la similarité entre deux réponses avec IA"""
        if not client:
            # Similarité basique (Levenshtein simplifié)
            return CheatingDetector._basic_similarity(answer1, answer2)
        
        try:
            prompt = f"""Compare ces deux réponses à la même question et calcule leur similarité (0-1) :

Question : {question}

Réponse 1 : {answer1}
Réponse 2 : {answer2}

Réponds UNIQUEMENT avec un nombre entre 0 et 1 représentant la similarité :
0 = complètement différent
1 = identique ou très similaire

Nombre uniquement :"""

            from app.services.ai_service import _get_max_tokens_param
            create_params = {
                "model": AI_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "Tu es un expert en détection de plagiat. Calcule la similarité entre réponses."
                    },
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1
            }
            create_params.update(_get_max_tokens_param(AI_MODEL, 10))
            response = await client.chat.completions.create(**create_params)
            
            similarity_text = response.choices[0].message.content.strip()
            try:
                similarity = float(similarity_text)
                return max(0.0, min(1.0, similarity))
            except ValueError:
                return CheatingDetector._basic_similarity(answer1, answer2)
                
        except Exception as e:
            logger.error(f"Erreur lors du calcul de similarité: {e}", exc_info=True)
            return CheatingDetector._basic_similarity(answer1, answer2)
    
    @staticmethod
    def _basic_similarity(answer1: str, answer2: str) -> float:
        """Similarité basique (Jaccard)"""
        words1 = set(answer1.lower().split())
        words2 = set(answer2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0


