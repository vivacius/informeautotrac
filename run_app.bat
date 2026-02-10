@echo off
echo ==========================================
echo   Productivity App - Setup & Run
echo ==========================================

echo [1/2] Installing required libraries...
"C:\Users\sacorreac\Downloads\.venv\Scripts\python.exe" -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo Error installing dependencies.
    pause
    exit /b
)

echo.
echo [2/2] Launching Streamlit App...
"C:\Users\sacorreac\Downloads\.venv\Scripts\python.exe" -m streamlit run app.py

if %errorlevel% neq 0 (
    echo Error launching the app.
)

pause
