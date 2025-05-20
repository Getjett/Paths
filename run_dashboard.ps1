Write-Host "Installing required packages..." -ForegroundColor Green
pip install -r requirements.txt

Write-Host "Starting Learning Tool Dashboard..." -ForegroundColor Green
python -m streamlit run app.py
