@echo off
chcp 65001 > nul

echo.
echo ==================================================
echo === Redémarrage du Backend ===
echo ==================================================
echo.

echo [1/3] Arrêt des processus utilisant le port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo Arrêt du processus PID %%a...
    taskkill /F /PID %%a >nul 2>&1
)
echo.

echo [2/3] Attente de 2 secondes...
timeout /t 2 /nobreak >nul
echo.

echo [3/3] Démarrage du backend...
cd backend
if exist venv\Scripts\python.exe (
    echo Backend démarré sur http://localhost:8000
    echo Appuyez sur Ctrl+C pour arrêter le serveur
    echo.
    call venv\Scripts\python.exe main.py
) else (
    echo Erreur: Environnement virtuel non trouve dans backend\venv
    pause
    exit /b 1
)




