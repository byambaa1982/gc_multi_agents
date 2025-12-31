# Start local FastAPI app
Write-Host "Starting FastAPI app locally..." -ForegroundColor Green
Write-Host "Navigate to http://localhost:8080 to test" -ForegroundColor Cyan
Write-Host "API docs available at: http://localhost:8080/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

& "$PSScriptRoot\venv\Scripts\python.exe" "$PSScriptRoot\app.py"
