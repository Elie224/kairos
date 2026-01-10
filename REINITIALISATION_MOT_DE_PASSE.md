# 🔐 Réinitialisation du Mot de Passe - Guide Complet

## ⚠️ Problème Actuel

L'erreur `ERR_CONNECTION_REFUSED` sur `localhost:5173` indique que **le serveur frontend n'est pas démarré**.

## ✅ Solution : Démarrer le Frontend

### Option 1 : Utiliser le script batch (CMD)
```cmd
cd frontend
demarrer-frontend.bat
```

### Option 2 : Démarrer manuellement
```cmd
cd frontend
npm run dev
```

### Option 3 : Utiliser PowerShell
```powershell
cd frontend
npm run dev
```

## 📋 Étapes Complètes pour Réinitialiser le Mot de Passe

### 1. Démarrer le Backend
Assurez-vous que le backend est démarré :
```cmd
cd backend
demarrer-backend.bat
```

Le backend doit être accessible sur `http://localhost:8000`

### 2. Démarrer le Frontend
Démarrez le frontend dans un **nouveau terminal** :
```cmd
cd frontend
npm run dev
```

Le frontend doit être accessible sur `http://localhost:5173`

### 3. Accéder à la Page "Mot de Passe Oublié"
1. Ouvrez votre navigateur
2. Allez sur : `http://localhost:5173/forgot-password`
3. Entrez votre email : `kouroumaelisee@gmail.com`
4. Cliquez sur "Envoyer le lien de réinitialisation"

### 4. Obtenir le Lien de Réinitialisation
En mode développement, le lien s'affichera directement dans l'interface :
- Un message de confirmation apparaîtra
- Un lien cliquable sera affiché
- Cliquez sur le lien ou le bouton "Réinitialiser mon mot de passe"

### 5. Définir le Nouveau Mot de Passe
1. Vous serez redirigé vers : `http://localhost:5173/reset-password?token=...`
2. Entrez votre nouveau mot de passe (minimum 8 caractères)
3. Confirmez le mot de passe
4. Cliquez sur "Réinitialiser le mot de passe"

### 6. Se Connecter
Après la réinitialisation :
1. Vous serez redirigé vers la page de connexion
2. Connectez-vous avec :
   - Email : `kouroumaelisee@gmail.com`
   - Nouveau mot de passe : celui que vous venez de définir

## 🔍 Vérifications

### Vérifier que le Backend est démarré
- Ouvrez : `http://localhost:8000/docs`
- Vous devriez voir la documentation Swagger de l'API

### Vérifier que le Frontend est démarré
- Ouvrez : `http://localhost:5173`
- Vous devriez voir la page d'accueil de Kaïros

## ⚠️ Problèmes Courants

### Frontend ne démarre pas
- Vérifiez que Node.js est installé : `node -v`
- Vérifiez que les dépendances sont installées : `cd frontend && npm install`
- Vérifiez que le port 5173 n'est pas utilisé par un autre processus

### Backend ne démarre pas
- Vérifiez que MongoDB est démarré
- Vérifiez que Python est installé
- Vérifiez que le venv est activé

### Le lien de réinitialisation ne fonctionne pas
- Vérifiez que le token n'a pas expiré (valide 1 heure)
- Vérifiez que le frontend et le backend sont bien démarrés
- Vérifiez les logs du backend pour voir les erreurs

## 📝 Notes

- En mode développement, le lien de réinitialisation s'affiche dans l'interface
- En production, le lien serait envoyé par email
- Le token est valide pendant 1 heure
- Le mot de passe doit contenir au moins 8 caractères
