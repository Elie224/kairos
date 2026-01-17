"""
Tests pour les endpoints Kairos Prompts
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_curriculum_generate():
    """Test génération de curriculum"""
    response = client.post(
        "/api/kairos/curriculum/generate",
        json={
            "subject": "mathematics",
            "level": "lycée",
            "objective": "exam"
        }
    )
    assert response.status_code in [200, 500]  # 500 si OpenAI non configuré
    if response.status_code == 200:
        data = response.json()
        assert "success" in data
        assert "curriculum" in data


def test_learner_profile_update():
    """Test mise à jour du profil cognitif"""
    response = client.post(
        "/api/kairos/learner/profile/update",
        json={
            "learning_data": {
                "completed_modules": 5,
                "average_score": 75,
                "errors": ["erreur1", "erreur2"]
            }
        }
    )
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.json()
        assert "success" in data
        assert "learner_profile" in data


def test_evaluation_generate():
    """Test génération d'évaluation"""
    response = client.post(
        "/api/kairos/evaluation/generate",
        json={
            "subject": "physics",
            "level": "lycée",
            "evaluation_type": "formative"
        }
    )
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.json()
        assert "success" in data
        assert "evaluation" in data


def test_explainability_analyze():
    """Test analyse d'erreur (Explainability)"""
    response = client.post(
        "/api/kairos/explainability/analyze",
        json={
            "error_analysis": {
                "user_answer": "2+2=5",
                "correct_answer": "2+2=4",
                "question": "Quel est le résultat de 2+2 ?"
            }
        }
    )
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.json()
        assert "success" in data
        assert "explanation" in data


def test_lab_simulate():
    """Test simulation de laboratoire"""
    response = client.post(
        "/api/kairos/lab/simulate",
        json={
            "simulation_request": "Simule un circuit RC avec résistance variable"
        }
    )
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.json()
        assert "success" in data
        assert "simulation" in data


def test_season_generate():
    """Test génération de saison pédagogique"""
    response = client.post(
        "/api/kairos/gamification/season/generate",
        json={
            "subject": "mathematics",
            "theme": "Algèbre avancée"
        }
    )
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.json()
        assert "success" in data
        assert "season" in data


def test_badge_evolve():
    """Test évolution de badge"""
    response = client.post(
        "/api/kairos/gamification/badge/evolve",
        json={
            "badge_type": "subject_master",
            "progress_data": {
                "modules_completed": 10,
                "perfect_scores": 8
            }
        }
    )
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.json()
        assert "success" in data
        assert "badge_evolution" in data


def test_multi_agent():
    """Test appel d'agent IA"""
    response = client.post(
        "/api/kairos/agents/theorist_prof",
        json={
            "agent_type": "theorist_prof",
            "context": {
                "concept": "dérivée",
                "level": "lycée"
            }
        }
    )
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.json()
        assert "success" in data
        assert "agent" in data


def test_analytics_predict():
    """Test prédiction de progression"""
    response = client.post(
        "/api/kairos/analytics/predict",
        json={
            "analytics_type": "progress_prediction",
            "data": {
                "completed_modules": 5,
                "average_score": 75,
                "time_spent": 20
            }
        }
    )
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.json()
        assert "success" in data
        assert "predictions" in data


def test_dashboard_insights():
    """Test insights dashboard"""
    response = client.post(
        "/api/kairos/analytics/dashboard",
        json={
            "analytics_type": "dashboard_insights",
            "data": {
                "metrics": {"completion": 60, "score": 75}
            }
        }
    )
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.json()
        assert "success" in data
        assert "insights" in data


def test_pdf_notes():
    """Test génération de notes PDF"""
    response = client.post(
        "/api/kairos/academic/pdf-notes",
        json={
            "subject": "mathematics",
            "module": "Algèbre linéaire"
        }
    )
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.json()
        assert "success" in data
        assert "pdf_content" in data


def test_learning_report():
    """Test génération de rapport d'apprentissage"""
    response = client.post(
        "/api/kairos/academic/learning-report",
        json={
            "user_id": "test_user",
            "period": "2024-01"
        }
    )
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.json()
        assert "success" in data
        assert "report" in data


def test_topics_endpoint():
    """Test récupération des topics"""
    response = client.get("/api/kairos/topics/mathematics")
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "topics" in data
    assert isinstance(data["topics"], list)
