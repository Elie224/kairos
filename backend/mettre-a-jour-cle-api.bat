@echo off
echo ========================================
echo   Mise a jour de la cle API OpenAI
echo ========================================
echo.
echo Cette operation va mettre a jour la cle API dans le fichier .env
echo.
pause

cd backend
.\venv\Scripts\python.exe scripts\update_openai_key.py

echo.
echo Mise a jour terminee.
echo.
echo IMPORTANT: Redemarrez le backend pour que les changements prennent effet.
pause
