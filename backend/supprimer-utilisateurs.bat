@echo off
REM Script pour supprimer tous les utilisateurs des bases de données
echo ========================================
echo   Suppression de tous les utilisateurs
echo ========================================
echo.
echo ATTENTION: Cette operation va supprimer TOUS les utilisateurs!
echo   - MongoDB: Collection 'users'
echo   - PostgreSQL: Table 'users' + donnees liees
echo.
pause

cd backend
call venv\Scripts\python.exe scripts\delete_all_users_complete.py --confirm

if %ERRORLEVEL% EQU 0 (
    echo.
    echo OK: Suppression terminee!
    echo.
    echo Vous pouvez maintenant creer un nouveau compte.
) else (
    echo.
    echo ERREUR lors de la suppression
)

pause
