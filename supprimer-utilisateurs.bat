@echo off
echo ========================================
echo   Suppression de tous les utilisateurs
echo ========================================
echo.
echo ATTENTION: Cette operation supprimera TOUS les utilisateurs !
echo.
pause

cd backend
call venv\Scripts\activate
python scripts\delete_all_users.py

pause
