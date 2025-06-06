# Quick Start Guide

Get started with SimpleEnvs in under 5 minutes! 🚀

## 30-Second Setup

### 1. Install
```bash
pip install simpleenvs-python
```

### 2. Create .env file
```bash
echo "APP_NAME=MyApp
DEBUG=true
PORT=8080
DATABASE_URL=postgresql://user:pass@localhost/db" > .env
```

### 3. Load and use
```python
from simpleenvs import load_dotenv
load_dotenv()

import os
print(f"App: {os.getenv('APP_NAME')}")  # MyApp
print(f"Debug: {os.getenv('DEBUG')}")   # True
print(f"Port: {os.getenv('PORT')}")     # 8080
```

**That's it!** You're now using SimpleEnvs. 🎉

## Basic Usage Patterns

### 🔄 Drop-in Replacement for python-dotenv

```python
# Before (python-dotenv)
from dotenv import load_dotenv
load_dotenv()

# After (SimpleEnvs) - Only change the import!
from simpleenvs import load_dotenv
load_dotenv()  # Same API, 2-4x faster! ⚡
```

### 🎯 Type-Safe Access

```python
import simpleenvs

simpleenvs.load_dotenv()

# Type-safe getters with defaults
app_name = simpleenvs.get_str('APP_NAME', 'DefaultApp')  # str
debug = simpleenvs.get_bool('DEBUG', False)             # bool  
port = simpleenvs.get_int('PORT', 8080)                 # int
timeout = simpleenvs.get_float('TIMEOUT', 30.0)         # float
```

### ⚡ Async Loading

```python
import simpleenvs

# Async loading (recommended for web apps)
await simpleenvs.load('.env')

# Or one-liner
from simpleenvs import aload_dotenv
await aload_dotenv()
```

### 🔒 Secure Mode (Enterprise)

```python
from simpleenvs import load_dotenv_secure, get_secure

# Memory-isolated loading (NOT in os.environ!)
load_dotenv_secure()

# Secure access
jwt_secret = get_secure('JWT_SECRET')
db_password = get_secure('DB_PASSWORD')

# Verify isolation
import os
print(os.getenv('JWT_SECRET'))  # None - properly isolated! 🔒
```

## Common Use Cases

### 🌐 Web Application

```python
# app.py
from simpleenvs import load_dotenv
from fastapi import FastAPI

# Load config
load_dotenv()

app = FastAPI()

@app.get("/")
def read_root():
    import os
    return {
        "app": os.getenv("APP_NAME", "MyApp"),
        "version": os.getenv("VERSION", "1.0.0"),
        "debug": os.getenv("DEBUG", "false").lower() == "true"
    }
```

### 🐳 Docker Application

```python
# config.py
import simpleenvs

# Auto-detect environment and load appropriate file
import os
env = os.getenv('ENVIRONMENT', 'development')

if env == 'production':
    simpleenvs.load_dotenv_secure('.env.production')  # Secure mode
else:
    simpleenvs.load_dotenv(f'.env.{env}')  # Simple mode

# Configuration class
class Config:
    APP_NAME = simpleenvs.get_str('APP_NAME', 'MyApp')
    DATABASE_URL = simpleenvs.get_secure('DATABASE_URL') if env == 'production' else simpleenvs.get_str('DATABASE_URL')
    DEBUG = simpleenvs.get_bool('DEBUG', env != 'production')
    PORT = simpleenvs.get_int('PORT', 8000)
```

### 🔧 Development vs Production

```python
# settings.py
import os
import simpleenvs

# Load based on environment
environment = os.getenv('ENVIRONMENT', 'development')

if environment == 'production':
    # Maximum security for production
    simpleenvs.load_dotenv_secure('.env.production')
    
    # Access sensitive data securely
    DATABASE_PASSWORD = simpleenvs.get_secure('DATABASE_PASSWORD')
    JWT_SECRET = simpleenvs.get_secure('JWT_SECRET')
    
else:
    # Simple loading for development
    simpleenvs.load_dotenv('.env.development')
    
    # Regular access for non-sensitive data
    DATABASE_PASSWORD = simpleenvs.get_str('DATABASE_PASSWORD')
    JWT_SECRET = simpleenvs.get_str('JWT_SECRET')

# Common settings (always available)
APP_NAME = simpleenvs.get_str('APP_NAME', 'MyApp')
DEBUG = simpleenvs.get_bool('DEBUG', environment == 'development')
```

## Smart Directory Scanning

SimpleEnvs automatically finds your .env files! 🔍

```bash
# Your project structure
my-project/
├── app.py                    # Run from here
├── config/
│   └── .env                 # ✅ Found automatically!
├── environments/
│   ├── .env.development     # ✅ Found automatically!
│   └── .env.production      # ✅ Found automatically!
└── docker/
    └── .env.docker          # ✅ Found automatically!
```

```python
# Zero configuration - finds first .env automatically
simpleenvs.load_dotenv()

# Or control the search
simpleenvs.load(max_depth=3)          # Search 3 levels deep
simpleenvs.load(max_depth=1)          # Current directory only
simpleenvs.load('custom.env', max_depth=0)  # Exact file, no search
```

## Environment File Examples

### Basic .env
```bash
# Application settings
APP_NAME=SimpleEnvs Demo
VERSION=1.0.0
DEBUG=true

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
DATABASE_POOL_SIZE=10

# API Keys (keep these secret!)
JWT_SECRET=your-super-secret-jwt-key
API_KEY=your-api-key-here

# Feature flags
ENABLE_LOGGING=true
ENABLE_CACHE=false
```

### Development .env.development
```bash
DEBUG=true
DATABASE_URL=postgresql://dev:dev@localhost:5432/myapp_dev
LOG_LEVEL=DEBUG
CACHE_TTL=60
```

### Production .env.production
```bash
DEBUG=false
DATABASE_URL=postgresql://prod_user:secure_pass@prod-db:5432/myapp
LOG_LEVEL=ERROR
CACHE_TTL=3600
JWT_SECRET=super-secure-production-secret
```

## Error Handling

```python
import simpleenvs
from simpleenvs import SimpleEnvsError

try:
    simpleenvs.load_dotenv()
    
    # Required environment variables
    database_url = simpleenvs.get_str('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL is required")
        
except FileNotFoundError:
    print("No .env file found - using defaults")
except SimpleEnvsError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Debugging and Inspection

```python
import simpleenvs

# Load environment
simpleenvs.load_dotenv()

# Check what's loaded
info = simpleenvs.get_info()
print(f"Loaded {info['total_keys']} environment variables")

# List all keys
all_keys = simpleenvs.get_all_keys()
print(f"Available keys: {all_keys}")

# Security info (for secure mode)
simpleenvs.load_dotenv_secure()
security_info = simpleenvs.get_security_info()
print(f"Security session: {security_info}")
```

## Framework Integration

### FastAPI
```python
from fastapi import FastAPI
import simpleenvs

app = FastAPI()

@app.on_event("startup")
async def startup():
    await simpleenvs.load('.env')
    print("Environment loaded!")

@app.get("/config")
def get_config():
    return {
        "app_name": simpleenvs.get_str("APP_NAME"),
        "debug": simpleenvs.get_bool("DEBUG"),
        "version": simpleenvs.get_str("VERSION", "1.0.0")
    }
```

### Django
```python
# settings.py
import simpleenvs

# Load environment at the top
simpleenvs.load_dotenv()

# Use in Django settings
import os
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
SECRET_KEY = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
```

### Flask
```python
from flask import Flask
import simpleenvs

# Load environment
simpleenvs.load_dotenv()

app = Flask(__name__)

# Configure from environment
app.config.from_object('config.Config')

@app.route('/')
def home():
    return f"Hello from {simpleenvs.get_str('APP_NAME')}!"
```

## Best Practices

### ✅ Do's
- Use `.env` for local development
- Use secure mode for production secrets
- Set sensible defaults with `get_*` functions
- Keep `.env` files out of version control
- Use environment-specific files (`.env.production`, `.env.development`)

### ❌ Don'ts
- Don't commit `.env` files to git
- Don't put production secrets in simple mode
- Don't use overly long variable names
- Don't forget to validate required variables

## Next Steps

Ready to dive deeper? 📚

1. **[API Reference](api-reference.md)** - Complete function documentation
2. **[Security Guide](security.md)** - Advanced security features
3. **[Examples](../examples/)** - Real-world usage examples
4. **[Migration Guide](migration.md)** - Moving from python-dotenv

## Need Help?

- 🐛 [Report Issues](https://github.com/vmintf/SimpleEnvs-Python/issues)
- 💬 [Ask Questions](https://github.com/vmintf/SimpleEnvs-Python/discussions)
- 📖 [Read Full Documentation](https://vmintf.github.io/SimpleEnvs-Python)

---

**Happy coding with SimpleEnvs!** 🚀✨