# Find Python installation on Windows
Write-Host "Searching for Python installations..." -ForegroundColor Cyan
Write-Host "====================================`n" -ForegroundColor Cyan

$pythonFound = $false

# Check common Python locations
$pythonPaths = @(
    "$env:LOCALAPPDATA\Programs\Python",
    "$env:PROGRAMFILES\Python*",
    "$env:PROGRAMFILES(X86)\Python*",
    "$env:USERPROFILE\AppData\Local\Programs\Python",
    "$env:USERPROFILE\AppData\Local\Microsoft\WindowsApps",
    "C:\Python*",
    "C:\Program Files\Python*"
)

Write-Host "Checking common installation paths..." -ForegroundColor Yellow
foreach ($basePath in $pythonPaths) {
    if (Test-Path $basePath) {
        $pythonDirs = Get-ChildItem -Path $basePath -Directory -ErrorAction SilentlyContinue
        foreach ($dir in $pythonDirs) {
            $pythonExe = Join-Path $dir.FullName "python.exe"
            if (Test-Path $pythonExe) {
                Write-Host "  ✓ Found: $pythonExe" -ForegroundColor Green
                $version = & $pythonExe --version 2>&1
                Write-Host "    Version: $version" -ForegroundColor Gray
                $pythonFound = $true
            }
        }
    }
}

# Check py launcher
Write-Host "`nChecking Python Launcher (py)..." -ForegroundColor Yellow
$pyLauncher = Get-Command py -ErrorAction SilentlyContinue
if ($pyLauncher) {
    Write-Host "  ✓ Python Launcher found: $($pyLauncher.Source)" -ForegroundColor Green
    $pyVersion = py --version 2>&1
    Write-Host "    Version: $pyVersion" -ForegroundColor Gray
    Write-Host "`n  You can use: py -m pip install -e ." -ForegroundColor Cyan
    $pythonFound = $true
} else {
    Write-Host "  ✗ Python Launcher not found" -ForegroundColor Red
}

# Check PATH
Write-Host "`nChecking PATH environment variable..." -ForegroundColor Yellow
$pathEntries = $env:PATH -split ';'
$pythonInPath = $false
foreach ($entry in $pathEntries) {
    if ($entry -like "*Python*" -and (Test-Path $entry)) {
        $pythonExe = Join-Path $entry "python.exe"
        if (Test-Path $pythonExe) {
            Write-Host "  ✓ Python in PATH: $entry" -ForegroundColor Green
            $pythonInPath = $true
        }
    }
}

if (-not $pythonInPath) {
    Write-Host "  ✗ Python not found in PATH" -ForegroundColor Red
}

# Check Microsoft Store Python
Write-Host "`nChecking Microsoft Store..." -ForegroundColor Yellow
$storePython = "$env:LOCALAPPDATA\Microsoft\WindowsApps\python.exe"
if (Test-Path $storePython) {
    Write-Host "  ✓ Microsoft Store Python found: $storePython" -ForegroundColor Green
    Write-Host "    Note: This may require Microsoft Store setup" -ForegroundColor Yellow
    $pythonFound = $true
}

# Recommendations
Write-Host "`n====================================`n" -ForegroundColor Cyan

if (-not $pythonFound) {
    Write-Host "Python is not installed or not found." -ForegroundColor Red
    Write-Host "`nPlease install Python 3.11+:" -ForegroundColor Yellow
    Write-Host "  1. Visit: https://www.python.org/downloads/" -ForegroundColor White
    Write-Host "  2. Download Python 3.11+ for Windows" -ForegroundColor White
    Write-Host "  3. During installation:" -ForegroundColor White
    Write-Host "     - Check 'Add Python to PATH'" -ForegroundColor Cyan
    Write-Host "     - Choose 'Install for all users' (if you have admin rights)" -ForegroundColor Cyan
    Write-Host "  4. Restart PowerShell/terminal after installation" -ForegroundColor White
} else {
    Write-Host "Python found! Try these commands:" -ForegroundColor Green
    Write-Host "`nOption 1 (if py launcher works):" -ForegroundColor Cyan
    Write-Host "  py -m pip install -e ." -ForegroundColor White
    
    Write-Host "`nOption 2 (if Python is in PATH after restart):" -ForegroundColor Cyan
    Write-Host "  python -m pip install -e ." -ForegroundColor White
    
    Write-Host "`nOption 3 (use full path - replace with your Python path):" -ForegroundColor Cyan
    Write-Host "  `$env:PATH += ';C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python311'" -ForegroundColor White
    Write-Host "  python -m pip install -e ." -ForegroundColor White
    
    Write-Host "`nIf Python is installed but not in PATH:" -ForegroundColor Yellow
    Write-Host "  1. Find Python installation (see paths above)" -ForegroundColor White
    Write-Host "  2. Add it to PATH manually:" -ForegroundColor White
    Write-Host "     - Search 'Environment Variables' in Windows" -ForegroundColor White
    Write-Host "     - Edit 'Path' variable" -ForegroundColor White
    Write-Host "     - Add Python directory and Scripts directory" -ForegroundColor White
    Write-Host "  3. Restart PowerShell" -ForegroundColor White
}

Write-Host "`n"

