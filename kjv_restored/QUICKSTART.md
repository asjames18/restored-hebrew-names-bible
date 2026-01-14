# Quick Start Guide

## 1. Install Python (if needed)

**Windows:**
- Download from https://www.python.org/downloads/
- **Important:** Check "Add Python to PATH" during installation
- Restart your terminal after installation

**Verify:**
```powershell
python --version
# Should show: Python 3.11.x or higher
```

**If Python is not found, run the diagnostic:**
```powershell
.\find_python.ps1
```

This will help you find Python installations or guide you to install it.

## 2. Install the Package

```powershell
cd kjv_restored
python -m pip install -e .
```

## 3. Run Your First Conversion

```powershell
# Convert sample text
python -m kjv_restored --in data\sample_input.txt --out output.txt

# View the result
cat output.txt
```

## 4. Try Different Formats

```powershell
# JSON format
python -m kjv_restored --in data\sample_verses.json --format json --out output.json

# With report
python -m kjv_restored --in data\sample_input.txt --out output.txt --report report.json
```

## 5. Run Tests

```powershell
# Install dev dependencies first
python -m pip install -e .[dev]

# Run tests
python -m pytest tests/
```

## Common Issues

**"Python was not found"**
- Python is not in your PATH
- Reinstall Python and check "Add Python to PATH"
- Or restart your terminal

**"pip is not recognized"**
- Use: `python -m pip install -e .`

**Import errors**
- Make sure you're in the `kjv_restored` directory
- Run: `python -m pip install -e .`

## Next Steps

- Read [README.md](README.md) for full documentation
- See [INSTALL.md](INSTALL.md) for detailed installation instructions
- Check `data/` folder for sample files

