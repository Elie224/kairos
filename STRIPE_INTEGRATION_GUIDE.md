# 💳 Guide d'Intégration Stripe - Kaïros

## ✅ Implémentation Complète

### Fonctionnalités Implémentées

1. ✅ **Création de sessions de checkout Stripe**
   - Plans Premium (19.99€/mois)
   - Plans Enterprise (49.99€/mois)
   - Abonnements récurrents mensuels

2. ✅ **Webhooks Stripe**
   - Gestion création abonnement
   - Mise à jour abonnement
   - Annulation abonnement
   - Paiements réussis/échoués

3. ✅ **Limites par plan**
   - Requêtes IA limitées par mois
   - Accès fonctionnalités selon plan
   - Vérification en temps réel

4. ✅ **Gestion abonnements**
   - Récupération plan utilisateur
   - Annulation abonnement
   - Vérification limites IA

---

## 🔧 Configuration Requise

### Variables d'Environnement

Ajoutez dans votre fichier `.env` :

```env
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_...  # Clé secrète Stripe
STRIPE_WEBHOOK_SECRET=whsec_...  # Secret webhook Stripe
STRIPE_PREMIUM_PRICE_ID=price_...  # ID prix Premium (optionnel)
STRIPE_ENTERPRISE_PRICE_ID=price_...  # ID prix Enterprise (optionnel)
```

### Installation

```bash
pip install stripe>=7.0.0
```

---

## 📋 Endpoints API

### 1. Récupérer les limites d'un plan
```
GET /api/subscriptions/plans/{plan}
```

### 2. Récupérer le plan actuel
```
GET /api/subscriptions/my-plan
```

### 3. Créer une session de checkout
```
POST /api/subscriptions/checkout
Body: {
    "plan": "premium" | "enterprise",
    "success_url": "https://...",
    "cancel_url": "https://..."
}
```

### 4. Webhook Stripe
```
POST /api/subscriptions/webhook
Headers: {
    "stripe-signature": "..."
}
```

### 5. Annuler un abonnement
```
POST /api/subscriptions/cancel
```

### 6. Vérifier limite IA
```
GET /api/subscriptions/check-ai-limit
```

### 7. Vérifier accès fonctionnalité
```
GET /api/subscriptions/check-feature/{feature}
```

---

## 🎯 Plans Disponibles

### FREE (Gratuit)
- 50 requêtes IA/mois
- Modules de base
- Quiz basiques
- 1 GB stockage
- Support standard

### PREMIUM (19.99€/mois)
- 500 requêtes IA/mois
- Tous les modules
- Tutorat IA
- Laboratoires virtuels
- Analytics avancés
- 10 GB stockage
- Support prioritaire

### ENTERPRISE (49.99€/mois)
- Requêtes IA illimitées
- Tous les modules
- Contenu personnalisé
- Accès API
- 100 GB stockage
- Support prioritaire

---

## 🔄 Flux de Paiement

1. **Utilisateur choisit un plan** → Frontend appelle `/api/subscriptions/checkout`
2. **Backend crée session Stripe** → Retourne URL de checkout
3. **Utilisateur paie sur Stripe** → Redirection vers `success_url`
4. **Stripe envoie webhook** → Backend crée abonnement en base
5. **Utilisateur utilise fonctionnalités** → Vérification limites en temps réel

---

## 🛡️ Vérification des Limites

### Dans les Services IA

Ajoutez cette vérification avant chaque requête IA :

```python
from app.services.subscription_service import SubscriptionService

# Vérifier limite avant requête IA
limits = await SubscriptionService.check_ai_limit(user_id)
if not limits["allowed"]:
    raise HTTPException(
        status_code=403,
        detail=f"Limite IA atteinte. Plan: {limits['plan']}, Restant: {limits['remaining']}"
    )

# Enregistrer la requête
await SubscriptionService.record_ai_request(user_id, "endpoint_name")
```

---

## 📊 Collections MongoDB

### `subscriptions`
- `user_id`: ID utilisateur
- `plan`: Plan (free/premium/enterprise)
- `stripe_subscription_id`: ID abonnement Stripe
- `stripe_customer_id`: ID client Stripe
- `status`: Statut (active/cancelled/expired)
- `start_date`: Date début
- `end_date`: Date fin
- `auto_renew`: Renouvellement automatique

### `ai_requests`
- `user_id`: ID utilisateur
- `endpoint`: Endpoint appelé
- `created_at`: Date requête

---

## 🧪 Tests

### Mode Test Stripe

Utilisez les clés de test Stripe :
- Clé secrète : `sk_test_...`
- Webhook secret : `whsec_...`

### Tester le Webhook Localement

Utilisez Stripe CLI :
```bash
stripe listen --forward-to localhost:8000/api/subscriptions/webhook
```

---

## ✅ Checklist Déploiement

- [ ] Variables d'environnement configurées
- [ ] Stripe installé (`pip install stripe`)
- [ ] Webhook configuré dans dashboard Stripe
- [ ] URLs de succès/annulation configurées
- [ ] Tests effectués en mode test
- [ ] Vérification limites intégrée dans services IA
- [ ] Monitoring des paiements configuré

---

*Guide créé pour l'intégration Stripe complète*











