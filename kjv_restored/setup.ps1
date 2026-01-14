# Setup script for KJV Restored Names Converter
# This script helps verify the environment and provides installation instructions

Write-Host "KJV Restored Names Converter - Setup Check" -ForegroundColor Cyan
Write-Host "==========================================`n" -ForegroundColor Cyan

# Check for Python
Write-Host "Checking for Python..." -ForegroundColor Yellow

# Try python command
$pythonFound = $false
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
    $pythonFound = $true
    
    # Check Python version
    $version = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>&1
    if ($version -match "^3\.(1[1-9]|[2-9][0-9])") {
        Write-Host "✓ Python version 3.11+ detected" -ForegroundColor Green
    } else {
        Write-Host "⚠ Warning: Python 3.11+ required, found $version" -ForegroundColor Yellow
    }
} else {
    # Try py launcher
    Write-Host "  Trying Python Launcher (py)..." -ForegroundColor Yellow
    $pyVersion = py --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Python Launcher found: $pyVersion" -ForegroundColor Green
        Write-Host "  You can use: py -m pip install -e ." -ForegroundColor Cyan
        $pythonFound = $true
    } else {
        Write-Host "✗ Python not found in PATH" -ForegroundColor Red
        Write-Host "`nRunning Python finder script..." -ForegroundColor Yellow
        if (Test-Path ".\find_python.ps1") {
            & ".\find_python.ps1"
        } else {
            Write-Host "  find_python.ps1 not found" -ForegroundColor Yellow
        }
        Write-Host "`nPlease install Python 3.11 or higher:" -ForegroundColor Yellow
        Write-Host "  1. Visit https://www.python.org/downloads/" -ForegroundColor White
        Write-Host "  2. Download Python 3.11+ for Windows" -ForegroundColor White
        Write-Host "  3. During installation, check 'Add Python to PATH'" -ForegroundColor White
        Write-Host "  4. Restart your terminal after installation`n" -ForegroundColor White
        exit 1
    }
}

# Check for pip
Write-Host "`nChecking for pip..." -ForegroundColor Yellow
$pipVersion = python -m pip --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ pip found: $pipVersion" -ForegroundColor Green
} else {
    Write-Host "✗ pip not found" -ForegroundColor Red
    Write-Host "  pip should come with Python. Try: python -m ensurepip --upgrade" -ForegroundColor Yellow
    exit 1
}

# Check project structure
Write-Host "`nChecking project structure..." -ForegroundColor Yellow
$requiredFiles = @(
    "src\kjv_restored\__init__.py",
    "src\kjv_restored\cli.py",
    "src\kjv_restored\converter.py",
    "pyproject.toml"
)

$allFilesExist = $true
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file (missing)" -ForegroundColor Red
        $allFilesExist = $false
    }
}

if (-not $allFilesExist) {
    Write-Host "`n✗ Some required files are missing" -ForegroundColor Red
    exit 1
}

Write-Host "`n✓ Project structure looks good!" -ForegroundColor Green

# Offer to install
Write-Host "`nInstallation Options:" -ForegroundColor Cyan
Write-Host "  1. Install in development mode: python -m pip install -e ." -ForegroundColor White
Write-Host "  2. Install in user mode: python -m pip install -e . --user" -ForegroundColor White
Write-Host "  3. Install with dev dependencies: python -m pip install -e .[dev]" -ForegroundColor White
Write-Host "`nAfter installation, you can run:" -ForegroundColor Cyan
Write-Host "  python -m kjv_restored --in data\sample_input.txt --out out.txt" -ForegroundColor White

# Test import
Write-Host "`nTesting imports..." -ForegroundColor Yellow
$testScript = @"
import sys
sys.path.insert(0, 'src')
try:
    from kjv_restored import RestoredNamesConverter
    print('✓ Import successful!')
except ImportError as e:
    print(f'✗ Import failed: {e}')
    sys.exit(1)
"@

$testResult = python -c $testScript 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host $testResult -ForegroundColor Green
} else {
    Write-Host $testResult -ForegroundColor Red
    Write-Host "`nNote: This is normal if the package isn't installed yet." -ForegroundColor Yellow
}

Write-Host "`nSetup check complete!`n" -ForegroundColor Cyan

