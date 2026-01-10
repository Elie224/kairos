@echo off
echo ========================================
echo   Promotion en Administrateur
echo ========================================
echo.
echo Email: kouroumaelisee@gmail.com
echo.
pause

cd backend
.\venv\Scripts\python.exe scripts\promote_admin_email.py

echo.
echo Promotion terminee.
pause
