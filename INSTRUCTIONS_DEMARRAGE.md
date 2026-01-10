# 🚀 Instructions de Démarrage - Application Kaïros

## ✅ État Actuel

- ✅ MongoDB : Démarré
- ✅ Environnement virtuel Python : Créé et dépendances installées
- ⏳ Backend : À démarrer
- ⏳ Frontend : À démarrer

---

## 🔧 Démarrer le Backend

### Option 1 : Script Batch (Recommandé)

**Double-cliquez sur** : `demarrer-backend.bat`

**OU dans un terminal** :
```cmd
demarrer-backend.bat
```

### Option 2 : Manuellement

Dans un terminal PowerShell ou CMD :

```cmd
cd backend
venv\Scripts\activate
python main.py
```

**Le backend sera accessible sur** : http://localhost:8000

---

## 🎨 Démarrer le Frontend

**Ouvrez un NOUVEAU terminal** et exécutez :

```cmd
cd frontend
npm install
npm run dev
```

**OU dans PowerShell** :
```powershell
cd frontend
npm install
npm run dev
```

**Le frontend sera accessible sur** : http://localhost:5173

---

## ✅ Vérification

Une fois les deux services démarrés :

1. **Backend Health Check** : http://localhost:8000/health
2. **Backend API Docs** : http://localhost:8000/docs
3. **Frontend** : http://localhost:5173

---

## 🐛 Résolution de Problèmes

### Backend : "ModuleNotFoundError"
```cmd
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

### Backend : "Connection refused" MongoDB
- Vérifiez que MongoDB est démarré : `docker ps | findstr mongodb`
- Vérifiez que le port 27017 est libre

### Frontend : "npm n'est pas reconnu"
- Installez Node.js depuis https://nodejs.org/
- Redémarrez votre terminal après l'installation

### Politique d'exécution PowerShell
Si vous avez des problèmes avec les scripts PowerShell, utilisez les scripts `.bat` à la place.

---

## 📝 Notes

- **Backend** : Gardez le terminal ouvert, appuyez sur `Ctrl+C` pour arrêter
- **Frontend** : Gardez le terminal ouvert, appuyez sur `Ctrl+C` pour arrêter
- **MongoDB** : Fonctionne en arrière-plan via Docker

---

**Bon développement ! 🚀**


