"""
Script de test pour les endpoints Kairos
Usage: python scripts/test_kairos_endpoints.py
"""
import requests
import json
import sys
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"  # Ajuster selon votre configuration
API_BASE = f"{BASE_URL}/api/kairos"

def test_endpoint(name: str, method: str, endpoint: str, data: Dict[str, Any] = None) -> bool:
    """Test un endpoint et affiche le résultat"""
    print(f"\n{'='*60}")
    print(f"🧪 Test: {name}")
    print(f"{'='*60}")
    print(f"Endpoint: {method} {endpoint}")
    
    try:
        if method == "GET":
            response = requests.get(f"{API_BASE}{endpoint}", timeout=5)
        elif method == "POST":
            response = requests.post(
                f"{API_BASE}{endpoint}",
                json=data or {},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
        else:
            print(f"❌ Méthode {method} non supportée")
            return False
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ Succès!")
                print(f"Response keys: {list(result.keys())}")
                if "success" in result:
                    print(f"Success: {result['success']}")
                return True
            except json.JSONDecodeError:
                print(f"⚠️  Réponse non-JSON: {response.text[:200]}")
                return False
        else:
            print(f"❌ Erreur: {response.status_code}")
            try:
                error = response.json()
                print(f"Error: {error}")
            except:
                print(f"Error text: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Impossible de se connecter à {BASE_URL}")
        print(f"   Assurez-vous que le serveur est démarré")
        return False
    except requests.exceptions.Timeout:
        print(f"⏱️  Timeout (requête trop longue)")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def main():
    """Exécute tous les tests"""
    print("🚀 Tests des endpoints Kairos")
    print(f"Base URL: {BASE_URL}")
    
    results = []
    
    # PRIORITÉ 1 - Curriculum
    results.append((
        "Curriculum Intelligent",
        test_endpoint(
            "Génération de curriculum",
            "POST",
            "/curriculum/generate",
            {
                "subject": "mathematics",
                "level": "lycée",
                "objective": "exam"
            }
        )
    ))
    
    # PRIORITÉ 2 - Profil Cognitif
    results.append((
        "Profil Cognitif",
        test_endpoint(
            "Mise à jour profil",
            "POST",
            "/learner/profile/update",
            {
                "learning_data": {
                    "completed_modules": 5,
                    "average_score": 75,
                    "errors": ["erreur1"]
                }
            }
        )
    ))
    
    # PRIORITÉ 3 - Évaluation
    results.append((
        "Évaluation Intelligente",
        test_endpoint(
            "Génération évaluation",
            "POST",
            "/evaluation/generate",
            {
                "subject": "physics",
                "level": "lycée",
                "evaluation_type": "formative"
            }
        )
    ))
    
    # PRIORITÉ 4 - Explainability
    results.append((
        "Explainability",
        test_endpoint(
            "Analyse d'erreur",
            "POST",
            "/explainability/analyze",
            {
                "error_analysis": {
                    "user_answer": "2+2=5",
                    "correct_answer": "2+2=4",
                    "question": "Quel est le résultat de 2+2 ?"
                }
            }
        )
    ))
    
    # PRIORITÉ 5 - Lab
    results.append((
        "Mode Laboratoire",
        test_endpoint(
            "Simulation lab",
            "POST",
            "/lab/simulate",
            {
                "simulation_request": "Simule un circuit RC avec résistance variable"
            }
        )
    ))
    
    # PRIORITÉ 6 - Gamification Avancée
    results.append((
        "Gamification Avancée",
        test_endpoint(
            "Génération saison",
            "POST",
            "/gamification/season/generate",
            {
                "subject": "mathematics",
                "theme": "Algèbre avancée"
            }
        )
    ))
    
    # PRIORITÉ 7 - Multi-Agents
    results.append((
        "Multi-Agents IA",
        test_endpoint(
            "Agent Prof Théoricien",
            "POST",
            "/agents/theorist_prof",
            {
                "agent_type": "theorist_prof",
                "context": {
                    "concept": "dérivée",
                    "level": "lycée"
                }
            }
        )
    ))
    
    # PRIORITÉ 8 - Analytics
    results.append((
        "Analytics",
        test_endpoint(
            "Prédiction progression",
            "POST",
            "/analytics/predict",
            {
                "analytics_type": "progress_prediction",
                "data": {
                    "completed_modules": 5,
                    "average_score": 75,
                    "time_spent": 20
                }
            }
        )
    ))
    
    # PRIORITÉ 9 - Contenu Académique
    results.append((
        "Contenu Académique",
        test_endpoint(
            "Notes PDF",
            "POST",
            "/academic/pdf-notes",
            {
                "subject": "mathematics",
                "module": "Algèbre linéaire"
            }
        )
    ))
    
    # Endpoints existants
    results.append((
        "Visualisation",
        test_endpoint(
            "Génération visualisation",
            "POST",
            "/visualization/generate",
            {
                "subject": "mathematics",
                "concept": "fonction quadratique",
                "level": "intermediate"
            }
        )
    ))
    
    results.append((
        "Topics",
        test_endpoint(
            "Récupération topics",
            "GET",
            "/topics/mathematics"
        )
    ))
    
    # Résumé
    print(f"\n{'='*60}")
    print("📊 RÉSUMÉ DES TESTS")
    print(f"{'='*60}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print(f"\n✅ Réussis: {passed}/{total}")
    print(f"❌ Échoués: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 Tous les tests sont passés!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) ont échoué")
        return 1


if __name__ == "__main__":
    sys.exit(main())
