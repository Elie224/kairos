# 🎨 Démarrer le Frontend - Guide Rapide

## ✅ Node.js Vérifié

Node.js v25.2.1 est installé et fonctionne ! ✅

---

## 🚀 Démarrer le Frontend

### Option 1 : Script Batch (Recommandé)

**Double-cliquez sur** : `demarrer-frontend.bat`

**OU dans un terminal CMD** :
```cmd
demarrer-frontend.bat
```

### Option 2 : Commandes Manuelles

**Ouvrez un terminal CMD** (pas PowerShell si npm ne fonctionne pas) :

```cmd
cd "C:\Users\KOURO\OneDrive\Desktop\Kairós"
cd frontend
npm install
npm run dev
```

---

## 📝 Notes Importantes

1. **Utilisez CMD** si PowerShell ne reconnaît pas npm
2. **Première fois** : `npm install` peut prendre quelques minutes
3. **Le frontend** sera accessible sur : http://localhost:5173

---

## ✅ Vérification

Une fois démarré, vous devriez voir :
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

---

## 🐛 Si npm n'est toujours pas reconnu

Dans PowerShell, ajoutez Node.js au PATH temporairement :

```powershell
$env:PATH += ";C:\Program Files\nodejs"
npm --version
```

Puis démarrez le frontend normalement.

---

**Bon développement ! 🚀**


