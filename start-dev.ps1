Write-Host "Starting FastAPI backend..."

Start-Process powershell -ArgumentList "cd backend; python -m uvicorn api_main:app --reload"

Write-Host "Starting Angular frontend..."

Start-Process powershell -ArgumentList "cd frontend/app; ng serve"

Write-Host "Development servers started."