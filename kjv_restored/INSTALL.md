# Installation Instructions

## Prerequisites

- Python 3.11 or higher
- pip (usually comes with Python)

## Quick Setup

### 1. Install Python (if not already installed)

**Windows:**
1. Visit https://www.python.org/downloads/
2. Download Python 3.11+ for Windows
3. **Important:** During installation, check the box "Add Python to PATH"
4. Complete the installation
5. Restart your terminal/PowerShell

**Verify installation:**
```powershell
python --version
# Should show: Python 3.11.x or higher
```

### 2. Install the Package

From the `kjv_restored` directory:

```powershell
# Install in development mode (recommended)
python -m pip install -e .

# Or install with development dependencies (for testing)
python -m pip install -e .[dev]
```

### 3. Verify Installation

```powershell
# Test the import
python -c "from kjv_restored import RestoredNamesConverter; print('Success!')"

# Or run the CLI
python -m kjv_restored --help
```

## Using the Setup Script

A PowerShell setup script is provided to check your environment:

```powershell
.\setup.ps1
```

This will:
- Check for Python installation
- Verify Python version
- Check for pip
- Verify project structure
- Test imports

## Troubleshooting

### "Python was not found"

1. **First, check if Python is actually installed:**
   ```powershell
   # Run the diagnostic script
   .\find_python.ps1
   ```
   This will search for Python installations on your system.

2. **If Python is installed but not in PATH:**
   
   **Option A: Use Python Launcher (py)**
   ```powershell
   # Check if py launcher works
   py --version
   
   # If it works, use it instead
   py -m pip install -e .
   ```
   
   **Option B: Add Python to PATH manually**
   - Find Python installation (usually `C:\Users\YourName\AppData\Local\Programs\Python\Python3xx`)
   - Press `Win + X` and select "System"
   - Click "Advanced system settings"
   - Click "Environment Variables"
   - Under "User variables" or "System variables", find "Path" and click "Edit"
   - Click "New" and add:
     - `C:\Users\YourName\AppData\Local\Programs\Python\Python3xx`
     - `C:\Users\YourName\AppData\Local\Programs\Python\Python3xx\Scripts`
   - Click "OK" on all dialogs
   - **Restart PowerShell**
   
   **Option C: Use full path temporarily**
   ```powershell
   # Find your Python path using find_python.ps1, then:
   & "C:\Users\YourName\AppData\Local\Programs\Python\Python311\python.exe" -m pip install -e .
   ```

3. **If Python is not installed:**
   - Visit https://www.python.org/downloads/
   - Download Python 3.11+ for Windows
   - **IMPORTANT:** During installation, check "Add Python to PATH"
   - Restart PowerShell after installation

### "pip is not recognized"

Try using:
```powershell
python -m pip install -e .
```

### Import Errors

If you get import errors, make sure you're in the `kjv_restored` directory and the package is installed:

```powershell
cd kjv_restored
python -m pip install -e .
```

## Development Setup

For development with testing:

```powershell
# Install with dev dependencies
python -m pip install -e .[dev]

# Run tests
python -m pytest tests/
```

## Alternative: Use Without Installation

You can also run the package without installing by adding the src directory to PYTHONPATH:

```powershell
$env:PYTHONPATH = "src"
python -m kjv_restored --in data\sample_input.txt --out out.txt
```

