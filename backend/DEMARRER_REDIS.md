# 🚀 Guide pour Démarrer Redis

Ce guide explique comment démarrer Redis pour résoudre l'erreur "connexion refusée".

## 🔍 Diagnostic

**Erreur actuelle** : `Error 22 connecting to localhost:6379. Le système distant a refusé la connexion réseau`

Cela signifie que Redis n'est pas démarré ou n'accepte pas les connexions.

## 🐳 Solution 1 : Docker (Recommandé)

### Démarrer Redis avec Docker

```bash
docker run -d -p 6379:6379 --name kairos-redis redis:7-alpine
```

### Vérifier que Redis est démarré

```bash
docker ps | findstr redis
```

Vous devriez voir quelque chose comme :
```
kairos-redis   redis:7-alpine   Up X minutes   0.0.0.0:6379->6379/tcp
```

### Tester la connexion Redis

```bash
docker exec -it kairos-redis redis-cli ping
```

Vous devriez voir : `PONG`

## 🪟 Solution 2 : Installation Windows Native

### Option A : Memurai (Redis pour Windows)

1. Téléchargez Memurai depuis : https://www.memurai.com/
2. Installez et démarrez le service Memurai
3. Il écoutera automatiquement sur le port 6379

### Option B : WSL2 avec Redis

Si vous avez WSL2 installé :

```bash
# Dans WSL2
sudo apt-get update
sudo apt-get install redis-server
sudo service redis-server start
```

## 🔧 Configuration

### 1. Créer/Mettre à jour le fichier `.env`

Dans `backend/.env`, ajoutez ou vérifiez :

```env
REDIS_URL=redis://localhost:6379/0
```

### 2. Vérifier la connexion

Redémarrez le backend et vous devriez voir :

```
✅ Redis connecté avec succès
```

Au lieu de :

```
⚠️  Redis non configuré - Cache désactivé
```

## 🔍 Vérification des Ports

### Windows PowerShell

```powershell
# Vérifier si le port 6379 est ouvert
Test-NetConnection -ComputerName localhost -Port 6379
```

Si cela échoue, Redis n'est pas démarré.

### Vérifier les processus Redis

```powershell
# Vérifier si Redis tourne dans Docker
docker ps | Select-String redis

# Vérifier les services Windows
Get-Service | Where-Object {$_.DisplayName -like "*redis*" -or $_.DisplayName -like "*memurai*"}
```

## 🛠️ Dépannage

### Problème : Port déjà utilisé

Si le port 6379 est déjà utilisé :

```bash
# Trouver quel processus utilise le port
netstat -ano | findstr :6379

# Ou avec PowerShell
Get-NetTCPConnection -LocalPort 6379
```

### Problème : Redis démarre mais la connexion échoue

1. Vérifiez que Redis écoute sur toutes les interfaces :
   ```bash
   docker run -d -p 0.0.0.0:6379:6379 --name kairos-redis redis:7-alpine
   ```

2. Vérifiez le firewall Windows :
   - Ouvrez le Pare-feu Windows
   - Autorisez le port 6379 pour les connexions entrantes

### Problème : Redis dans Docker mais connexion refusée

Vérifiez que le port est bien mappé :

```bash
docker port kairos-redis
```

Vous devriez voir : `6379/tcp -> 0.0.0.0:6379`

## 📝 Configuration Redis Avancée

### Redis avec mot de passe (optionnel)

Si vous voulez sécuriser Redis avec un mot de passe :

```bash
docker run -d -p 6379:6379 --name kairos-redis redis:7-alpine redis-server --requirepass votre_mot_de_passe
```

Puis dans `.env` :
```env
REDIS_URL=redis://:votre_mot_de_passe@localhost:6379/0
```

### Redis avec persistance

```bash
docker run -d -p 6379:6379 \
  -v redis-data:/data \
  --name kairos-redis \
  redis:7-alpine \
  redis-server --appendonly yes
```

## ✅ Vérification Finale

Après avoir démarré Redis, testez la connexion :

```bash
# Depuis le backend
cd backend
python -c "import redis; r = redis.Redis(host='localhost', port=6379, db=0); print(r.ping())"
```

Vous devriez voir : `True`

Ou utilisez le script de test :

```bash
python scripts/test_connections.py
```

## 🎯 Commandes Utiles

### Arrêter Redis

```bash
docker stop kairos-redis
```

### Redémarrer Redis

```bash
docker restart kairos-redis
```

### Voir les logs Redis

```bash
docker logs kairos-redis
```

### Accéder au CLI Redis

```bash
docker exec -it kairos-redis redis-cli
```

Puis vous pouvez tester :
```
PING
INFO
KEYS *
```

## 📚 Ressources

- Documentation Redis : https://redis.io/docs/
- Docker Hub Redis : https://hub.docker.com/_/redis
- Memurai (Redis pour Windows) : https://www.memurai.com/








