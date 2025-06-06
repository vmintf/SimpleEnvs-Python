# Installation Guide

## Requirements

### Python Version
- **Python 3.7+** (recommended: Python 3.9+)
- Compatible with Python 3.7, 3.8, 3.9, 3.10, 3.11, 3.12

### System Requirements
- **Operating Systems**: Windows, macOS, Linux
- **Memory**: Minimal requirements (< 10MB)
- **Dependencies**: `aiofiles` (automatically installed)

## Installation Methods

### 📦 PyPI (Recommended)

```bash
pip install simpleenvs-python
```

### 📋 Requirements.txt

Add to your `requirements.txt`:
```
simpleenvs-python>=1.0.0
```

Then install:
```bash
pip install -r requirements.txt
```

### 🔒 Poetry

```bash
poetry add simpleenvs-python
```

### 📝 Pipenv

```bash
pipenv install simpleenvs-python
```

### 🔧 Development Installation

For contributing or development:

```bash
# Clone repository
git clone https://github.com/vmintf/SimpleEnvs-Python.git
cd simpleenvs

# Install in development mode
pip install -e ".[dev]"

# Or with poetry
poetry install --with dev
```

## Verification

### Quick Test

```python
# test_installation.py
import simpleenvs

# Check version
print(f"SimpleEnvs version: {simpleenvs.__version__}")

# Quick functionality test
print("Installation successful! ✅")
```

### Advanced Test

```python
# Create test .env file
with open('.env', 'w') as f:
    f.write('TEST_VAR=hello_world\nDEBUG=true\n')

# Test loading
import simpleenvs
simpleenvs.load_dotenv()

import os
print(f"TEST_VAR: {os.getenv('TEST_VAR')}")  # Should print: hello_world
print(f"DEBUG: {os.getenv('DEBUG')}")        # Should print: True

# Clean up
os.remove('.env')
```

## Migration from python-dotenv

SimpleEnvs is designed as a **drop-in replacement** for python-dotenv:

### Before (python-dotenv)
```python
from dotenv import load_dotenv
load_dotenv()
```

### After (SimpleEnvs)
```python
from simpleenvs import load_dotenv
load_dotenv()  # Same API, 2-4x faster! 🚀
```

**That's it!** No other changes needed.

## Optional Dependencies

### For Development
```bash
pip install simpleenvs-python[dev]
```

Includes:
- `pytest` - Testing framework
- `black` - Code formatting
- `isort` - Import sorting
- `mypy` - Type checking

### For Testing
```bash
pip install simpleenvs-python[test]
```

Includes:
- `pytest`
- `pytest-cov` - Coverage reporting
- `pytest-asyncio` - Async testing

## Common Issues & Solutions

### Issue: "Module not found"
```bash
ModuleNotFoundError: No module named 'simpleenvs'
```

**Solutions:**
1. Ensure correct package name: `pip install simpleenvs-python` (not `simpleenvs`)
2. Check virtual environment: `which python` and `which pip`
3. Reinstall: `pip uninstall simpleenvs-python && pip install simpleenvs-python`

### Issue: Import Error
```python
ImportError: cannot import name 'load_dotenv' from 'simpleenvs'
```

**Solutions:**
1. Check installation: `pip show simpleenvs-python`
2. Try importing differently:
   ```python
   import simpleenvs
   simpleenvs.load_dotenv()
   ```

### Issue: Permission Error (Windows)
```
PermissionError: [WinError 5] Access is denied
```

**Solutions:**
1. Run as administrator
2. Use user installation: `pip install --user simpleenvs-python`
3. Use virtual environment

### Issue: SSL Certificate Error
```
SSL: CERTIFICATE_VERIFY_FAILED
```

**Solutions:**
1. Upgrade pip: `python -m pip install --upgrade pip`
2. Use trusted host: `pip install --trusted-host pypi.org simpleenvs-python`

## Virtual Environment Setup

### Using venv (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install SimpleEnvs
pip install simpleenvs-python
```

### Using conda
```bash
# Create environment
conda create -n myproject python=3.9

# Activate
conda activate myproject

# Install SimpleEnvs
pip install simpleenvs-python
```

## Docker Installation

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install SimpleEnvs
RUN pip install simpleenvs-python

COPY . .

CMD ["python", "app.py"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  app:
    build: .
    environment:
      - ENVIRONMENT=production
    volumes:
      - ./.env:/app/.env
```

## Performance Verification

Run the built-in benchmark to verify performance improvements:

```bash
# at project root folder
python benchmark.py
```

Expected output:
```
SimpleEnvs vs python-dotenv Performance Comparison
==================================================
Testing with 100 variables...
python-dotenv: 8.04ms
SimpleEnvs:    2.17ms
Speedup:       3.7x faster ⚡
```

## Environment-Specific Installation

### Production
```bash
pip install simpleenvs-python --no-dev
```

### Development
```bash
pip install simpleenvs-python[dev]
```

### CI/CD
```bash
pip install simpleenvs-python[test]
```

## Next Steps

After successful installation:

1. 📖 Read the [Quick Start Guide](quickstart.md)
2. 🔍 Explore [API Reference](api-reference.md)
3. 🔒 Learn about [Security Features](security.md)
4. 🚀 Check out [examples/](../examples/)

## Getting Help

If you encounter any installation issues:

1. 🐛 [Report a bug](https://github.com/vmintf/SimpleEnvs-Python/issues)
2. 💬 [Join discussions](https://github.com/vmintf/SimpleEnvs-Python/discussions)
3. 📧 [Contact support](mailto:vmintf@gmail.com)

---

**Installation successful?** Time to [get started](quickstart.md) with SimpleEnvs! 🎉