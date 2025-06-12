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

# Type-safe getters with automatic conversion
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
    # Async loading - perfect for modern Python apps
    await simpleenvs.load()
    
    # Access variables
    db_url = simpleenvs.get_str('DATABASE_URL')
    print(f"Database: {db_url}")

# Run async
asyncio.run(main())
```

## 6. Secure Mode (Enterprise) 🔒

For sensitive data that should **never** touch `os.environ`:

```python
import simpleenvs
import os

# Load with maximum security (memory-isolated)
simpleenvs.load_dotenv_secure()

# Access secure variables (NOT in os.environ!)
api_key = simpleenvs.get_secure('API_KEY')
db_password = simpleenvs.get_secure('DATABASE_PASSWORD')

# Verify security isolation
print(f"API Key loaded: {api_key is not None}")
print(f"In os.environ: {os.getenv('API_KEY')}")  # None - properly isolated! 🔒
```

**Security Benefits:**
- ✅ Memory isolation - secrets never touch system environment
- ✅ Access logging for security auditing
- ✅ File integrity verification with SHA-256
- ✅ Protection against path traversal attacks

## 7. Auto-Discovery

SimpleEnvs automatically finds your .env files:

```bash
# Your project structure
my-project/
├── app.py                    # Run from here
├── .env                      # ✅ Found automatically!
├── config/
│   └── .env.production       # ✅ Found automatically!
├── environments/
│   └── .env.development      # ✅ Found automatically!
└── docker/
    └── .env.docker          # ✅ Found automatically!
```

```python
# No path needed - auto-discovery!
from simpleenvs import load_dotenv
load_dotenv()  # Finds the first .env file automatically
```

## 8. Performance Comparison ⚡

**SimpleEnvs vs python-dotenv benchmark results:**

| Variables | python-dotenv | SimpleEnvs | **Speedup** |
|-----------|---------------|-------------|-------------|
| 10 vars | 2.0ms | 0.1ms | **13.5x faster** ⚡ |
| 100 vars | 10.9ms | 0.4ms | **28.3x faster** ⚡ |
| 1000 vars | 105.1ms | 5.0ms | **20.9x faster** ⚡ |
| 5000 vars | 633.3ms | 72.5ms | **8.7x faster** ⚡ |

*Real benchmark data from our test suite*

## 9. Common Patterns

### Web Application Startup

```python
# main.py
import simpleenvs
from fastapi import FastAPI

app = FastAPI()

@app.on_event("startup")
async def startup():
    # Load public configuration
    await simpleenvs.load()
    
    # Load secrets securely (memory-isolated)
    await simpleenvs.load_secure()

@app.get("/")
def read_root():
    return {
        "app": simpleenvs.get_str("APP_NAME"),
        "version": simpleenvs.get_str("VERSION", "1.0.0"),
        # Secure data remains isolated
        "has_secrets": simpleenvs.get_secure("JWT_SECRET") is not None
    }
```

### Environment-Specific Loading

```python
import os
import simpleenvs

# Auto-detect environment
env = os.getenv('ENVIRONMENT', 'development')
simpleenvs.load_dotenv(f'.env.{env}')

# Use environment-specific settings
debug = simpleenvs.get_bool('DEBUG')
db_url = simpleenvs.get_str('DATABASE_URL')
```

### Configuration Class

```python
import simpleenvs

class Config:
    def __init__(self):
        simpleenvs.load_dotenv()
        
        # Public configuration
        self.app_name = simpleenvs.get_str('APP_NAME', 'MyApp')
        self.debug = simpleenvs.get_bool('DEBUG', False)
        self.port = simpleenvs.get_int('PORT', 8080)
        
        # Load secrets separately
        simpleenvs.load_dotenv_secure()
        self.jwt_secret = simpleenvs.get_secure('JWT_SECRET')

# Usage
config = Config()
print(f"Starting {config.app_name} on port {config.port}")
```

## 10. Migration from python-dotenv

**Instant migration** - just change the import:

```python
# Before (python-dotenv)
from dotenv import load_dotenv
load_dotenv()

# After (SimpleEnvs) - Only change the import!
from simpleenvs import load_dotenv
load_dotenv()  # Same API, 2-28x faster performance! ⚡
```

**That's it!** Your existing code works unchanged with massive performance gains.

## 11. Quick Performance Test

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
# Expected: ~5ms (vs python-dotenv: ~105ms - 20x faster!)
```

## 12. Error Handling

```python
import simpleenvs

try:
    simpleenvs.load_dotenv()
    
    # Validate required variables
    required_vars = ['DATABASE_URL', 'API_KEY']
    for var in required_vars:
        if not simpleenvs.get_str(var):
            raise ValueError(f"Missing required environment variable: {var}")
            
except FileNotFoundError:
    print("No .env file found - using defaults")
except simpleenvs.SimpleEnvsError as e:
    print(f"Configuration error: {e}")
```

## 13. Best Practices ✅

### ✅ Do This

```python
# Use type-safe getters with defaults
debug = simpleenvs.get_bool('DEBUG', False)
port = simpleenvs.get_int('PORT', 8080)
timeout = simpleenvs.get_int('TIMEOUT', 30)

# Use secure mode for sensitive data
jwt_secret = simpleenvs.get_secure('JWT_SECRET')
api_key = simpleenvs.get_secure('API_KEY')

# Provide meaningful defaults
app_name = simpleenvs.get_str('APP_NAME', 'MyApplication')
```

### ❌ Avoid This

```python
# Don't rely on manual string conversion
port = int(os.getenv('PORT'))  # Can crash if PORT is not set!

# Don't expose secrets in system environment
os.environ['SECRET_KEY'] = secret  # Visible to all processes ⚠️

# Don't hardcode configuration
database_url = "postgresql://..."  # Not flexible ❌
```

## 14. Advanced Features

### Cross-Module Access

```python
# main.py - Load secrets once
import simpleenvs
await simpleenvs.load_secure('.env.production')

# utils.py - Automatic access
import simpleenvs
api_key = simpleenvs.get_secure('API_KEY')  # Works automatically! 🎯
```

### Security Monitoring

```python
# Get security information
info = simpleenvs.get_security_info()
print(f"Session ID: {info['session_id']}")
print(f"Access count: {info['access_count']}")

# Verify file integrity
loader = simpleenvs.SecureEnvLoader()
if loader.verify_file_integrity('.env'):
    print("✅ File integrity verified")
else:
    print("⚠️ File may have been tampered with")
```

## 15. IDE Setup

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

## 16. Security Best Practices 🛡️

### Separate Public and Private Config

```python
import simpleenvs

# Public configuration (can be in os.environ)
await simpleenvs.load('config.env')
app_name = simpleenvs.get_str('APP_NAME')

# Sensitive secrets (memory-isolated)
await simpleenvs.load_secure('secrets.env')
jwt_secret = simpleenvs.get_secure('JWT_SECRET')

# Verify secrets are NOT in os.environ
import os
assert os.getenv('JWT_SECRET') is None  # ✅ Properly isolated
```

### Environment-Specific Security

```python
import os
env = os.getenv('ENVIRONMENT', 'development')

if env == 'production':
    # Maximum security in production
    await simpleenvs.load_secure(strict=True)
else:
    # Development flexibility
    await simpleenvs.load(strict=False)
```

## 17. Next Steps

🎉 **Congratulations!** You're now using SimpleEnvs effectively.

**Continue learning:**
- 📖 [API Reference](api-reference.md) - Complete function documentation
- 🔒 [Security Guide](security.md) - Advanced security features  
- 🏗️ [Examples](../examples/) - Real-world usage examples
- ⚡ [Benchmark Suite](../benchmark.py) - Run your own performance tests

**Need help?**
- 🐛 [Report issues](https://github.com/vmintf/SimpleEnvs-Python/issues)
- 💬 [Join discussions](https://github.com/vmintf/SimpleEnvs-Python/discussions)
- 📧 [Contact support](mailto:vmintf@gmail.com)

---

**Ready to level up?** Explore [security features](security.md) for enterprise-grade protection! 🔒