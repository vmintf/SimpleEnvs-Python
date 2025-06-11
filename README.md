# SimpleEnvs

![PyPI - Version](https://img.shields.io/pypi/v/simpleenvs-python?label=PyPI%20Package)
[![Python](https://img.shields.io/pypi/pyversions/simpleenvs-python.svg)](https://pypi.org/project/simpleenvs-python/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![PyPI Downloads](https://static.pepy.tech/badge/simpleenvs-python)](https://pepy.tech/projects/simpleenvs-python)
[![CI Pipeline](https://github.com/vmintf/SimpleEnvs-Python/actions/workflows/ci.yml/badge.svg)](https://github.com/vmintf/SimpleEnvs-Python/actions/workflows/ci.yml)
[![Security Vulnerability Tests](https://github.com/vmintf/SimpleEnvs-Python/actions/workflows/security_tests.yml/badge.svg)](https://github.com/vmintf/SimpleEnvs-Python/actions/workflows/security_tests.yml)

> **Ultra-secure, high-performance .env file loader for Python**  
> *Drop-in replacement for python-dotenv with enterprise security and 2-40x performance*

## 🚀 Why SimpleEnvs?

- 🏃‍♂️ **2-40x faster** than python-dotenv (verified benchmarks)
- 🔒 **Enterprise-grade security** with memory isolation
- 🎯 **Automatic type conversion** (int, bool, float)
- ⚡ **Zero configuration** - works out of the box
- 🔄 **100% python-dotenv compatible** API
- 🔍 **Smart directory scanning** - finds .env files automatically

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
load_dotenv()  # Same API, up to 40x faster! 🚀
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

## 📊 Performance
[![Performance Benchmark](https://github.com/vmintf/SimpleEnvs-Python/actions/workflows/benchmark.yml/badge.svg)](https://github.com/vmintf/SimpleEnvs-Python/actions/workflows/benchmark.yml)

**Latest GitHub Actions benchmark results:**

| Variables | File Size | python-dotenv | SimpleEnvs Standard | **SimpleEnvs Secure** | **Speedup** |
|-----------|-----------|---------------|---------------------|------------------------|-------------|
| 10 vars | 482B | 2.0ms | 0.1ms | **0.4ms** | **13.5x faster** ⚡ |
| 50 vars | 1.3KB | 5.9ms | 0.2ms | **0.5ms** | **23.8x faster** ⚡ |
| 100 vars | 2.4KB | 10.9ms | 0.4ms | **0.6ms** | **28.3x faster** ⚡ |
| 500 vars | 11KB | 51.3ms | 2.0ms | **1.7ms** | **26.1x faster** ⚡ |
| 1000 vars | 22KB | 105.1ms | 5.0ms | **2.7ms** | **20.9x faster** ⚡ |
| 5000 vars | 111KB | 633.3ms | 72.5ms | **12.5ms** | **8.7x faster** 🚀 |

**Key discovery**: Secure mode (with enterprise security) can be **faster** than standard mode on larger files!

**Test yourself:**
```bash
# Run the same benchmark as our CI
python -m simpleenvs.benchmark --quick

# Include secure mode testing
python -m simpleenvs.benchmark --secure
```

## 🔒 Security Features

### Simple Mode (Default)
Perfect for development and most production use cases:

```python
from simpleenvs import load_dotenv
load_dotenv()  # Variables stored in os.environ
```

### Secure Mode (Enterprise)
[![Security Vulnerability Tests](https://github.com/vmintf/SimpleEnvs-Python/actions/workflows/security_tests.yml/badge.svg)](https://github.com/vmintf/SimpleEnvs-Python/actions/workflows/security_tests.yml)

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

### 🛡️ Security Test Matrix

| Attack Vector | Tests | Status | Protection Level |
|---------------|-------|---------|------------------|
| **Path Traversal** | 8/8 ✅ | `../../../etc/passwd` | 🔴 **BLOCKED** |
| **Script Injection** | 7/7 ✅ | `<script>alert('xss')` | 🔴 **BLOCKED** |
| **Command Injection** | 7/7 ✅ | `$(rm -rf /)` | 🔴 **BLOCKED** |
| **File Size Attacks** | 4/4 ✅ | 15MB+ malicious files | 🔴 **BLOCKED** |
| **Memory Security** | 3/3 ✅ | Isolation verification | 🟢 **SECURED** |
| **Type Safety** | 5/5 ✅ | Invalid conversions | 🟡 **HANDLED** |
| **Edge Cases** | 17/17 ✅ | Unicode, encoding, etc. | 🟢 **ROBUST** |

### Security Testing

```bash
# Run comprehensive security tests
python -m simpleenvs.vuln_test

# Sample threats automatically blocked:
# ❌ ../../../etc/passwd           # Path traversal
# ❌ <script>alert('xss')</script> # Script injection  
# ❌ $(rm -rf /)                   # Command injection
# ❌ 15MB+ malicious files         # DoS attacks
# ✅ Memory isolation verified     # Enterprise security
# 📊 Total: 51/51 tests passed (100% success rate)
```

## 🔍 Smart Directory Scanning

**Unlike python-dotenv, SimpleEnvs automatically finds your .env files:**

```bash
# Your project structure
my-project/
├── app.py                    # Run from here
├── config/
│   └── .env                 # ✅ Found automatically!
├── environments/
│   └── .env.production      # ✅ Found automatically!
└── docker/
    └── .env.docker          # ✅ Found automatically!
```

```python
# SimpleEnvs (auto-discovery)
from simpleenvs import load_dotenv
load_dotenv()  # Finds the first .env file automatically!

# Manual control when needed
load_dotenv('.env.production')         # Specific file
load_dotenv('config/database.env')     # Custom path
simpleenvs.load(max_depth=3)          # Search deeper
```

## 🎯 Advanced Features

### Async Support

```python
import simpleenvs

# Async loading
await simpleenvs.load('.env')
await simpleenvs.load_secure('.env')

# Or one-liner
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
    # Public config
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
```

### Environment-Specific Loading

```python
import simpleenvs

# Auto-detect environment
env = os.getenv('ENVIRONMENT', 'development')
simpleenvs.load_dotenv(f'.env.{env}')

# Production with security
simpleenvs.load_dotenv_secure('.env.production')
```

## 🆚 SimpleEnvs vs python-dotenv

| Feature | python-dotenv | SimpleEnvs |
|---------|---------------|------------|
| **Performance** | Baseline | **2-40x faster** ⚡ |
| **Type Safety** | Manual casting | **Automatic** 🎯 |
| **Security** | Basic | **Enterprise-grade** 🔒 |
| **Memory Isolation** | ❌ | **✅ Secure mode** |
| **Async Support** | ❌ | **✅ Full support** |
| **Auto-discovery** | ❌ | **✅ Smart scanning** |
| **API Compatibility** | ✅ | **✅ Drop-in replacement** |

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

# Quick test (3 rounds)
python -m simpleenvs.benchmark --quick

# Include secure mode testing  
python -m simpleenvs.benchmark --secure

# More rounds for accuracy
python -m simpleenvs.benchmark --rounds 10
```

### Security Testing
```bash
# Comprehensive security tests
python -m simpleenvs.vuln_test

# Tests path traversal, injection attacks, memory isolation, etc.
# 51 security tests covering enterprise threat scenarios
```

## 🏗️ Use Cases

### Development
```python
# Quick setup
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

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](Contributing.md) for guidelines.

### Development Setup
```bash
# Clone repository
git clone https://github.com/vmintf/SimpleEnvs-Python.git
cd SimpleEnvs-Python

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
- Project originated from Zig [SimpleEnvs](https://github.com/vmintf/SimpleEnvs)

## 📚 Learn More

- 📖 [Full Documentation](https://vmintf.github.io/SimpleEnvs-Python)
- 🐛 [Issue Tracker](https://github.com/vmintf/SimpleEnvs-Python/issues)
- 💬 [Discussions](https://github.com/vmintf/SimpleEnvs-Python/discussions)
- 📦 [PyPI Package](https://pypi.org/project/simpleenvs-python/)

---

<div align="center">

**Made with ❤️ for the Python community**

*Simple to use, enterprise-grade security, proven performance* 🚀

</div>