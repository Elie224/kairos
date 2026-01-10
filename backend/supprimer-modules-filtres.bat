@echo off
echo ========================================
echo   Suppression des modules filtres
echo ========================================
echo.
echo ATTENTION: Cette operation supprimera 56 modules !
echo.
echo Modules a CONSERVER:
echo   - Informatique: Machine Learning uniquement
echo   - Mathematiques: Algebre Lineaire et Statistiques ^& Probabilites
echo.
pause

cd backend
.\venv\Scripts\python.exe scripts\delete_modules_filtered.py --confirm

echo.
echo Suppression terminee.
pause
