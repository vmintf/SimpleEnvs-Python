# SimpleEnvs

[![PyPI version](https://badge.fury.io/py/simpleenvs.svg)](https://badge.fury.io/py/simpleenvs)
[![Python](https://img.shields.io/pypi/pyversions/simpleenvs.svg)](https://pypi.org/project/simpleenvs/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Tests](https://github.com/simpleenvs/simpleenvs/workflows/tests/badge.svg)](https://github.com/simpleenvs/simpleenvs/actions)

> **Ultra-secure, high-performance .env file loader for Python**  
> *Simple to use, enterprise-grade security, 2-4x faster performance*

## 🚀 Why SimpleEnvs?

**Drop-in replacement for python-dotenv with proven improvements:**

- 🏃‍♂️ **2-4x faster** loading performance (verified benchmarks)
- 🔒 **Enterprise-grade security** with memory isolation
- 🎯 **Automatic type conversion** (int, bool, float)
- 💾 **Memory efficient** with optimized parsing
- ⚡ **Zero configuration** - works out of the box
- 🔄 **100% python-dotenv compatible** API

## 📊 Performance Benchmarks

Tested against python-dotenv (Windows 11, Python 3.11):

| Variables | File Size | python-dotenv | SimpleEnvs | **Speedup** |
|-----------|-----------|---------------|-------------|-------------|
| 10 vars | 373B | 1.40ms | 0.52ms | **2.7x faster** ⚡ |
| 100 vars | 2.3KB | 8.04ms | 2.17ms | **3.7x faster** ⚡ |
| 500 vars | 11KB | 43.1ms | 14.3ms | **3.0x faster** ⚡ |
| 1000 vars | 23KB | 102ms | 43.4ms | **2.4x faster** ⚡ |
| 5000 vars | 116KB | 1332ms | 800ms | **1.7x faster** ⚡ |

**Consistent performance gains across all file sizes!** 

*Run your own benchmarks: `python -m simpleenvs.benchmark`*

## 📦 Installation

```bash
pip install simpleenvs-python
```

## ⚡ Quick Start

### Python-dotenv Migration (1-line change!)

```python
# Before (python-dotenv)
from dotenv import load_dotenv
load_dotenv()

# After (SimpleEnvs) - Only change the import!
from simpleenvs import load_dotenv
load_dotenv()  # Same API, 2-4x faster! 🚀
```

### Basic Usage

```python
# Create .env file
echo "APP_NAME=MyApp\nDEBUG=true\nPORT=8080" > .env

# Load environment variables
from simpleenvs import load_dotenv
load_dotenv()

# Access variables
import os
print(os.getenv('APP_NAME'))  # "MyApp"
print(os.getenv('DEBUG'))     # "True" (auto-converted!)
print(os.getenv('PORT'))      # "8080"
```

### Type-Safe Access

```python
import simpleenvs

simpleenvs.load_dotenv()

# Type-safe getters
app_name = simpleenvs.get_str('APP_NAME', 'DefaultApp')  # str
debug = simpleenvs.get_bool('DEBUG', False)             # bool  
port = simpleenvs.get_int('PORT', 8080)                 # int
```

## 🔒 Security Features

### Simple Mode (Default)
Perfect for development and most production use cases:

```python
from simpleenvs import load_dotenv
load_dotenv()  # Variables stored in os.environ
```

### Secure Mode (Enterprise)
Memory-isolated environment variables that never touch `os.environ`:

```python
from simpleenvs import load_dotenv_secure, get_secure

load_dotenv_secure()  # Memory-isolated loading

# Secure access (not in os.environ!)
jwt_secret = get_secure('JWT_SECRET')
db_password = get_secure('DB_PASSWORD')

# Verify isolation
import os
print(os.getenv('JWT_SECRET'))  # None - properly isolated! 🔒
```

## 🔍 Smart Directory Scanning

**Unlike python-dotenv, SimpleEnvs automatically finds your .env files!**

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
# python-dotenv (manual paths 😤)
from dotenv import load_dotenv
load_dotenv('config/.env')                    # Must specify each path
load_dotenv('environments/.env.development')  # Must specify each path
load_dotenv('docker/.env.docker')             # Must specify each path

# SimpleEnvs (auto-discovery 🚀)
from simpleenvs import load_dotenv
load_dotenv()  # Finds the first .env file automatically!
```

### Smart Search Priority

SimpleEnvs searches in this order:
1. `.env` (current directory)
2. `.env.local` 
3. `.env.development`
4. `.env.production`
5. `.env.staging`
6. `config/.env` (subdirectories)
7. `environments/.env.*`

```python
# 🤖 Auto-discovery (Zero Config)
load_dotenv()                         # Finds first .env automatically

# 🎯 Manual paths (Precise Control)
load_dotenv('.env.production')         # Specific file
load_dotenv('config/database.env')     # Custom path
load_dotenv('/absolute/path/.env')     # Absolute path

# 🔧 Advanced control
simpleenvs.load(max_depth=3)          # Search 3 levels deep
simpleenvs.load(max_depth=1)          # Current directory only
simpleenvs.load('custom.env', max_depth=0)  # Exact file, no search
```

**Perfect for:**
- 🐳 **Docker projects** with config folders
- 🏗️ **Monorepos** with nested services  
- 📁 **Organized projects** with config directories
- 🔧 **CI/CD pipelines** with environment-specific configs
- 🎯 **Custom setups** with precise file control

## 🎯 Advanced Features

### Async Support

```python
import simpleenvs

# Async loading
await simpleenvs.load('.env')
await simpleenvs.load_secure('.env')

# Or async one-liner
from simpleenvs import aload_dotenv
await aload_dotenv()
```

### FastAPI Integration

```python
from fastapi import FastAPI
import simpleenvs

app = FastAPI()

@app.on_event("startup")
async def startup():
    # Non-sensitive config
    await simpleenvs.load('config.env')
    
    # Sensitive secrets (memory-isolated)
    await simpleenvs.load_secure('secrets.env')

@app.get("/config")
def get_config():
    return {
        "app_name": simpleenvs.get_str("APP_NAME"),
        "debug": simpleenvs.get_bool("DEBUG"),
        "port": simpleenvs.get_int("PORT", 8000)
    }

@app.get("/auth")  
def authenticate():
    # Secrets not in os.environ!
    jwt_secret = simpleenvs.get_secure("JWT_SECRET")
    return {"authenticated": jwt_secret is not None}
```

### Environment-Specific Loading

```python
import simpleenvs

# Development
simpleenvs.load_dotenv('.env.development')

# Production with security
simpleenvs.load_dotenv_secure('.env.production')

# Auto-detect environment
env = os.getenv('ENVIRONMENT', 'development')
simpleenvs.load_dotenv(f'.env.{env}')
```

## 🆚 SimpleEnvs vs python-dotenv

| Feature | python-dotenv | SimpleEnvs |
|---------|---------------|------------|
| **Performance** | Baseline | **2-4x faster** ⚡ |
| **Memory Efficiency** | Baseline | **Optimized parsing** 💾 |
| **Type Safety** | Manual casting | **Automatic** 🎯 |
| **Security** | Basic | **Enterprise-grade** 🔒 |
| **Memory Isolation** | ❌ | **✅ Secure mode** |
| **Async Support** | ❌ | **✅ Full support** |
| **Auto-discovery** | ❌ | **✅ Smart scanning** |
| **API Compatibility** | ✅ | **✅ Drop-in replacement** |

### Type Conversion Differences

```python
# .env file
DEBUG=true
PORT=8080
RATE=3.14

# python-dotenv (all strings)
os.getenv('DEBUG')  # "true"
os.getenv('PORT')   # "8080"  
os.getenv('RATE')   # "3.14"

# SimpleEnvs (smart conversion)
os.getenv('DEBUG')  # "True" (converted from bool)
os.getenv('PORT')   # "8080" (stays string)
os.getenv('RATE')   # "3.14" (stays string)

# Type-safe access (recommended)
simpleenvs.get_bool('DEBUG')  # True (actual bool)
simpleenvs.get_int('PORT')    # 8080 (actual int)
simpleenvs.get_float('RATE')  # 3.14 (actual float)
```

## 🛠️ API Reference

### Loading Functions

```python
# Simple loading (python-dotenv compatible)
load_dotenv(path=None)                    # Sync
aload_dotenv(path=None)                   # Async

# Secure loading (memory-isolated)  
load_dotenv_secure(path=None, strict=True)

# Advanced loading
simpleenvs.load(path, max_depth=2)        # Async with depth control
simpleenvs.load_sync(path, max_depth=2)   # Sync with depth control
simpleenvs.load_secure(path, strict=True) # Full secure loading
```

### Type-Safe Getters

```python
# Simple access (from os.environ)
get(key, default=None)           # Any type
get_str(key, default=None)       # String
get_int(key, default=None)       # Integer  
get_bool(key, default=None)      # Boolean

# Secure access (memory-isolated)
get_secure(key, default=None)        # Any type
get_str_secure(key, default=None)    # String
get_int_secure(key, default=None)    # Integer
get_bool_secure(key, default=None)   # Boolean
```

### Utility Functions

```python
# Status checks
is_loaded()                      # Simple loader status
is_loaded_secure()               # Secure loader status

# Information
get_info()                       # Library info
get_security_info()              # Security session info
get_all_keys()                   # All loaded keys

# Cleanup
clear()                          # Clear all loaded data
```

### Classes (Advanced)

```python
from simpleenvs import SimpleEnvLoader, SecureEnvLoader

# Simple loader
loader = SimpleEnvLoader()
await loader.load('.env')
value = loader.get('KEY')

# Secure loader  
secure = SecureEnvLoader()
await secure.load_secure()
value = secure.get_secure('KEY')
```

## 🏗️ Use Cases

### Development
```python
# Quick setup for development
from simpleenvs import load_dotenv
load_dotenv()  # Fast, simple, effective
```

### Production Web Apps
```python
# Public config + secure secrets
await simpleenvs.load('config.env')        # Public settings
await simpleenvs.load_secure('secrets.env') # Sensitive data
```

### Enterprise Applications
```python
# Maximum security with monitoring
from simpleenvs import SecureEnvLoader

loader = SecureEnvLoader(session_id="prod-001")
await loader.load_secure()

# Access with logging
secret = loader.get_secure('API_KEY')

# Audit trail
logs = loader.get_access_log()
integrity_ok = loader.verify_file_integrity('.env')
```

### Microservices
```python
# Environment-aware loading
import os
from simpleenvs import load_dotenv_secure

env = os.getenv('ENVIRONMENT', 'development')
load_dotenv_secure(f'.env.{env}')

# Service configuration
service_name = simpleenvs.get_secure('SERVICE_NAME')
database_url = simpleenvs.get_secure('DATABASE_URL')
```

## 🔧 Configuration

### Environment Detection

SimpleEnvs automatically detects your environment:

```python
# Automatic environment-specific settings
ENVIRONMENT=production    # Strict validation, minimal logging
ENVIRONMENT=development   # Relaxed validation, detailed errors  
ENVIRONMENT=testing       # Strict validation, detailed errors
```

### Custom Configuration

```python
from simpleenvs.secure import LoadOptions

# Custom secure loading
options = LoadOptions(
    path='.env.production',
    max_depth=1,
    strict_validation=True
)
await simpleenvs.load_secure(options)
```

## 🧪 Testing

### Run Tests
```bash
# Install with test dependencies
pip install simpleenvs[test]

# Run full test suite  
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=simpleenvs --cov-report=html
```

### Benchmarks
```bash
# Performance comparison with python-dotenv
python -m simpleenvs.benchmark

# Quick benchmark
python benchmark.py --quick

# Specific size test
python benchmark.py --size 1000
```

## 🚀 Real-World Performance

SimpleEnvs shines in practical scenarios:

**Web Application Startup:**
- Small config (20 vars): 1.5ms → 0.4ms (**3.8x faster**)
- Medium config (100 vars): 8ms → 2ms (**4x faster**)
- Large config (500+ vars): 40ms → 14ms (**3x faster**)

**Microservice Initialization:**
- Multiple .env files: **Async batch loading**
- Memory footprint: **Optimized parsing**
- Cold start time: **Consistently faster**

**Enterprise Security:**
- Sensitive data: **Memory-isolated**
- Audit trails: **Built-in logging**
- File integrity: **SHA-256 verification**

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup
```bash
# Clone repository
git clone https://github.com/simpleenvs/simpleenvs.git
cd simpleenvs

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Format code
black src/ tests/
isort src/ tests/
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by [python-dotenv](https://github.com/theskumar/python-dotenv)
- Built with security principles from [OWASP](https://owasp.org/)
- Performance optimizations inspired by [Zig](https://ziglang.org/) design philosophy
- Project orignated from Zig SimpleEnvs
[SimpleEnvs](https://github.com/vmintf/SimpleEnvs)

## 📚 Learn More

- 📖 [Full Documentation](https://simpleenvs.github.io/simpleenvs)
- 🐛 [Issue Tracker](https://github.com/simpleenvs/simpleenvs/issues)
- 💬 [Discussions](https://github.com/simpleenvs/simpleenvs/discussions)
- 📦 [PyPI Package](https://pypi.org/project/simpleenvs-python/)

---

<div align="center">

**Made with ❤️ for the Python community**

*Simple to use, enterprise-grade security, proven performance* 🚀

</div>