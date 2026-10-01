@echo off
cd /d "%~dp0"
echo ===================================================
echo   Real Estate Price Outlier Analyzer
echo ===================================================
echo.
echo Installing requirements (if needed)...
python -m pip install -r requirements.txt
echo.
echo Launching Streamlit Application...
python -m streamlit run app.py
pause
