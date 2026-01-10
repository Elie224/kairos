# ✅ Redis Configuré et Fonctionnel

## 🎉 Statut

**Redis est maintenant démarré et fonctionne correctement !**

## 📊 Informations

- **Conteneur** : `kairos-redis`
- **Image** : `redis:7-alpine`
- **Port** : `6379`
- **Status** : ✅ En cours d'exécution
- **URL** : `redis://localhost:6379/0`

## 🔍 Vérification

### Vérifier que Redis est démarré

```powershell
docker ps | Select-String redis
```

Vous devriez voir :
```
kairos-redis   redis:7-alpine   Up X minutes   0.0.0.0:6379->6379/tcp
```

### Tester la connexion

```powershell
cd backend
.\venv\Scripts\python.exe scripts\test_redis_connection.py
```

Ou via Docker :
```powershell
docker exec kairos-redis redis-cli ping
```

Vous devriez voir : `PONG`

## 🚀 Démarrage Automatique

Redis est configuré pour redémarrer automatiquement avec `--restart unless-stopped`.

## 📝 Commandes Utiles

### Démarrer Redis (si arrêté)

```powershell
docker start kairos-redis
```

Ou utilisez le script :
```powershell
cd backend
.\demarrer-redis.bat
```

### Arrêter Redis

```powershell
docker stop kairos-redis
```

### Redémarrer Redis

```powershell
docker restart kairos-redis
```

### Voir les logs

```powershell
docker logs kairos-redis
```

### Accéder au CLI Redis

```powershell
docker exec -it kairos-redis redis-cli
```

Dans le CLI, vous pouvez :
- `PING` - Tester la connexion
- `INFO` - Voir les informations
- `KEYS *` - Lister toutes les clés
- `FLUSHALL` - Vider toutes les données (ATTENTION!)

## ✅ Configuration dans .env

Vérifiez que votre fichier `backend/.env` contient :

```env
REDIS_URL=redis://localhost:6379/0
```

## 🎯 Prochaines Étapes

Redémarrez le backend pour que Redis soit utilisé :

```powershell
cd backend
.\demarrer-backend.bat
```

Vous devriez maintenant voir dans les logs :
```
✅ Redis connecté - Cache activé (performance optimale)
```

Au lieu de :
```
⚠️  Redis non configuré - Cache désactivé
```

## 🔧 Dépannage

### Redis ne démarre pas

1. Vérifiez que Docker est démarré
2. Vérifiez que le port 6379 n'est pas utilisé :
   ```powershell
   Get-NetTCPConnection -LocalPort 6379
   ```

### Connexion refusée

1. Vérifiez que le conteneur est en cours d'exécution :
   ```powershell
   docker ps | Select-String redis
   ```

2. Redémarrez Redis :
   ```powershell
   docker restart kairos-redis
   ```

### Port déjà utilisé

Si le port 6379 est déjà utilisé par un autre processus :

1. Trouvez le processus :
   ```powershell
   Get-NetTCPConnection -LocalPort 6379
   ```

2. Arrêtez-le ou utilisez un autre port (modifiez la commande Docker)

## 📚 Documentation

- Guide complet : `backend/DEMARRER_REDIS.md`
- Script de démarrage : `backend/demarrer-redis.bat`
- Script de test : `backend/scripts/test_redis_connection.py`
