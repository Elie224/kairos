@echo off
echo ========================================
echo   Suppression de tous les utilisateurs
echo ========================================
echo.

cd backend
call venv\Scripts\activate
python scripts\delete_all_users_simple.py

pause
