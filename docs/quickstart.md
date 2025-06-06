# Quick Start Guide

Get up and running with SimpleEnvs in 5 minutes! 🚀

## 1. Installation

```bash
pip install simpleenvs-python
```

## 2. Create Your First .env File

Create a file named `.env` in your project root:

```bash
# .env
APP_NAME=MyAwesomeApp
DEBUG=true
PORT=8080
DATABASE_URL=postgresql://user:pass@localhost/mydb
API_KEY=secret-key-here
```

## 3. Basic Usage

### Simple Loading (Most Common)

```python
# app.py
from simpleenvs import load_dotenv
import os

# Load .env file
load_dotenv()

# Access variables
app_name = os.getenv('APP_NAME')
debug = os.getenv('DEBUG')
port = int(os.getenv('PORT', 8080))

print(f"Starting {app_name} on port {port}")
print(f"Debug mode: {debug}")
```

**Run it:**
```bash
python app.py
```

**Output:**
```
Starting MyAwesomeApp on port 8080
Debug mode: True
```

## 4. Type-Safe Access (Recommended)

```python
import simpleenvs

# Load environment
simpleenvs.load_dotenv()

# Type-safe getters
app_name = simpleenvs.get_str('APP_NAME', 'DefaultApp')  # str
debug = simpleenvs.get_bool('DEBUG', False)             # bool
port = simpleenvs.get_int('PORT', 8080)                 # int

print(f"App: {app_name} | Debug: {debug} | Port: {port}")
```

## 5. Async Usage

```python
import asyncio
import simpleenvs

async def main():
    # Async loading
    await simpleenvs.load()
    
    # Access variables
    db_url = simpleenvs.get_str('DATABASE_URL')
    print(f"Database: {db_url}")

# Run async
asyncio.run(main())
```

## 6. Secure Mode (Enterprise)

For sensitive data that should **never** touch `os.environ`:

```python
import simpleenvs

# Load with maximum security (memory-isolated)
simpleenvs.load_dotenv_secure()

# Access secure variables (NOT in os.environ!)
api_key = simpleenvs.get_secure('API_KEY')
db_password = simpleenvs.get_secure('DATABASE_PASSWORD')

# Verify security
import os
print(os.getenv('API_KEY'))  # None - properly isolated! 🔒
```

## 7. Auto-Discovery

SimpleEnvs automatically finds your .env files:

```bash
# Your project structure
my-project/
├── app.py                    # Run from here
├── .env                      # ✅ Found automatically!
├── config/
│   └── .env.production       # ✅ Found automatically!
└── environments/
    └── .env.development      # ✅ Found automatically!
```

```python
# No path needed - auto-discovery!
from simpleenvs import load_dotenv
load_dotenv()  # Finds the first .env file automatically
```

## 8. Common Patterns

### Web Application Startup

```python
# main.py
import simpleenvs
from fastapi import FastAPI

app = FastAPI()

@app.on_event("startup")
async def startup():
    # Load configuration
    await simpleenvs.load()
    
    # Load secrets securely
    await simpleenvs.load_secure()

@app.get("/")
def read_root():
    return {
        "app": simpleenvs.get_str("APP_NAME"),
        "version": simpleenvs.get_str("VERSION", "1.0.0")
    }
```

### Environment-Specific Loading

```python
import os
import simpleenvs

# Auto-detect environment
env = os.getenv('ENVIRONMENT', 'development')
simpleenvs.load_dotenv(f'.env.{env}')

# Now use environment-specific settings
debug = simpleenvs.get_bool('DEBUG')
db_url = simpleenvs.get_str('DATABASE_URL')
```

### Configuration Class

```python
import simpleenvs

class Config:
    def __init__(self):
        simpleenvs.load_dotenv()
        
        self.app_name = simpleenvs.get_str('APP_NAME', 'MyApp')
        self.debug = simpleenvs.get_bool('DEBUG', False)
        self.port = simpleenvs.get_int('PORT', 8080)
        self.database_url = simpleenvs.get_str('DATABASE_URL')

# Usage
config = Config()
print(f"Starting {config.app_name} on port {config.port}")
```

## 9. Migration from python-dotenv

**Instant migration** - just change the import:

```python
# Before (python-dotenv)
from dotenv import load_dotenv
load_dotenv()

# After (SimpleEnvs) - Only change the import!
from simpleenvs import load_dotenv
load_dotenv()  # 2-4x faster performance! ⚡
```

**That's it!** Your existing code works unchanged.

## 10. Performance Comparison

Create a test with many variables to see the speed difference:

```python
# benchmark_test.py
import time
from simpleenvs import load_dotenv

# Create large .env file
with open('.env.test', 'w') as f:
    for i in range(1000):
        f.write(f'VAR_{i}=value_{i}\n')

# Benchmark loading
start_time = time.time()
load_dotenv('.env.test')
load_time = (time.time() - start_time) * 1000

print(f"Loaded 1000 variables in {load_time:.2f}ms")
# Expected: ~43ms (vs python-dotenv: ~102ms)
```

## 11. Error Handling

```python
import simpleenvs

try:
    simpleenvs.load_dotenv()
    
    # Required variables
    required_vars = ['DATABASE_URL', 'API_KEY']
    for var in required_vars:
        if not simpleenvs.get_str(var):
            raise ValueError(f"Missing required environment variable: {var}")
            
except FileNotFoundError:
    print("No .env file found - using defaults")
except Exception as e:
    print(f"Configuration error: {e}")
```

## 12. Best Practices

### ✅ Do This

```python
# Use type-safe getters
debug = simpleenvs.get_bool('DEBUG', False)
port = simpleenvs.get_int('PORT', 8080)

# Provide sensible defaults
timeout = simpleenvs.get_int('TIMEOUT', 30)

# Use secure mode for sensitive data
api_key = simpleenvs.get_secure('API_KEY')
```

### ❌ Avoid This

```python
# Don't rely on string conversion
port = int(os.getenv('PORT'))  # Can crash!

# Don't expose secrets in system environment
os.environ['SECRET_KEY'] = secret  # Visible to all processes

# Don't hardcode paths
load_dotenv('/absolute/path/.env')  # Not portable
```

## 13. IDE Setup

### VS Code Settings

Add to `.vscode/settings.json`:
```json
{
    "python.envFile": "${workspaceFolder}/.env",
    "python.defaultInterpreterPath": "./venv/bin/python"
}
```

### PyCharm Setup

1. Go to **Run/Debug Configurations**
2. Add **Environment Variables**
3. Click **Load from file** → Select `.env`

## 14. Next Steps

🎉 **Congratulations!** You're now using SimpleEnvs effectively.

**Continue learning:**
- 📖 [API Reference](api-reference.md) - Complete function documentation
- 🔒 [Security Guide](security.md) - Advanced security features
- 🏗️ [Best Practices](best-practices.md) - Production-ready patterns
- 🔧 [Examples](../examples/) - Real-world usage examples

**Need help?**
- 🐛 [Report issues](https://github.com/vmintf/SimpleEnvs-Python/issues)
- 💬 [Join discussions](https://github.com/vmintf/SimpleEnvs-Python/discussions)
- 📚 [Read full docs](https://vmintf.github.io/SimpleEnvs-Python)

---

**Ready to level up?** Explore [security features](security.md) for enterprise-grade protection! 🔒