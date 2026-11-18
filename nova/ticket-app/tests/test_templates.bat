@echo off
REM Script de test pour vérifier le système de templates PDF

echo ========================================
echo   TEST SYSTEME DE TEMPLATES PDF
echo ========================================
echo.

echo [1/4] Verification du dossier ticket_templates...
if exist "ticket_templates" (
    echo ✓ Dossier ticket_templates existe
) else (
    echo ✗ ERREUR: Dossier ticket_templates manquant
    exit /b 1
)
echo.

echo [2/4] Verification des templates PDF...
set count=0
if exist "ticket_templates\ensamien.pdf" (
    echo ✓ Template ensamien.pdf trouve
    set /a count+=1
) else (
    echo ⚠ Template ensamien.pdf non trouve ^(optionnel^)
)

if exist "ticket_templates\adherent.pdf" (
    echo ✓ Template adherent.pdf trouve
    set /a count+=1
) else (
    echo ⚠ Template adherent.pdf non trouve ^(optionnel^)
)

if exist "ticket_templates\externe.pdf" (
    echo ✓ Template externe.pdf trouve
    set /a count+=1
) else (
    echo ⚠ Template externe.pdf non trouve ^(optionnel^)
)

echo.
echo Nombre de templates trouves: %count%/3
echo.

echo [3/4] Verification de la bibliotheque pypdf...
.venv\Scripts\python.exe -c "import pypdf; print('✓ pypdf installe')" 2>nul
if errorlevel 1 (
    echo ✗ pypdf non installe
    echo Installation en cours...
    .venv\Scripts\pip.exe install pypdf
)
echo.

echo [4/4] Test de generation avec fichier test...
echo Copie de test_ticket_types.csv vers guest_list.csv...
copy /Y test_ticket_types.csv guest_list.csv >nul

echo Generation des tickets de test...
.venv\Scripts\python.exe generate_tickets.py --no-email --no-sms

if errorlevel 1 (
    echo ✗ ERREUR lors de la generation
    exit /b 1
) else (
    echo ✓ Generation reussie
)
echo.

echo ========================================
echo   RESULTAT DU TEST
echo ========================================
echo.
echo Verifiez les tickets generes dans le dossier 'tickets\'
echo.

if %count%==3 (
    echo ✓ TOUS LES TEMPLATES SONT EN PLACE
    echo   Les tickets auront 2 pages ^(template + QR^)
) else (
    echo ⚠ TEMPLATES MANQUANTS: %count%/3
    echo   Les tickets auront 1 page ^(QR uniquement^)
    echo   Placez vos PDFs dans ticket_templates\ pour activer les templates
)
echo.

echo Fichiers generes:
dir /B tickets\*.pdf 2>nul

echo.
echo Pour voir un ticket, ouvrez:
echo   tickets\test-ensamien.pdf
echo   tickets\test-adherent.pdf
echo   tickets\test-externe.pdf
echo.

pause
