@echo off
REM Copy required libraries from Python site-packages to dist folder

echo Copying export libraries to distribution...

REM Get the version number
set /p CURRENT_VERSION=<version.txt

REM Dynamically get site-packages path using Python
for /f "delims=" %%i in ('py -3.14 -c "import sys; print([p for p in sys.path if 'site-packages' in p][0])"') do set SRC_BASE=%%i

if not defined SRC_BASE (
    echo ERROR: Could not find Python 3.14 site-packages
    echo Please ensure Python 3.14 is installed and accessible via 'py -3.14'
    exit /b 1
)

echo [INFO] Using site-packages from: %SRC_BASE%
set DIST_FOLDER=dist\LiteFinPad_v%CURRENT_VERSION%\_internal

REM Create _internal folder if it doesn't exist
if not exist "%DIST_FOLDER%" (
    mkdir "%DIST_FOLDER%"
)

REM Copy xlsxwriter
echo Copying xlsxwriter...
if exist "%SRC_BASE%\xlsxwriter" (
    xcopy /E /I /Y "%SRC_BASE%\xlsxwriter" "%DIST_FOLDER%\xlsxwriter"
    echo xlsxwriter copied
) else (
    echo ERROR: xlsxwriter not found at %SRC_BASE%\xlsxwriter
)

REM Copy fpdf (old library, no PIL dependency)
echo Copying fpdf...
if exist "%SRC_BASE%\fpdf" (
    xcopy /E /I /Y "%SRC_BASE%\fpdf" "%DIST_FOLDER%\fpdf"
    echo fpdf copied
) else (
    echo ERROR: fpdf not found at %SRC_BASE%\fpdf
)

echo.
echo Library copying complete!

