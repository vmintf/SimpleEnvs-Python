# SimpleEnvs Documentation

Welcome to SimpleEnvs - the ultra-secure, high-performance .env file loader for Python!

```{eval-rst}
.. |version| replace:: |release|

.. image:: https://badge.fury.io/py/simpleenvs-python.svg
   :target: https://badge.fury.io/py/simpleenvs-python
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/simpleenvs-python.svg
   :target: https://pypi.org/project/simpleenvs-python/
   :alt: Python versions

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://github.com/vmintf/SimpleEnvs-Python/blob/main/LICENSE
   :alt: License

.. image:: https://img.shields.io/badge/version-|release|-blue.svg
   :target: https://github.com/vmintf/SimpleEnvs-Python/releases
   :alt: Current Version

.. image:: https://img.shields.io/badge/security-enterprise%20grade-green.svg
   :target: https://github.com/vmintf/SimpleEnvs-Python/actions/workflows/security_tests.yml
   :alt: Security Grade
```
> ⚠️ **Beta Documentation**: This is documentation for SimpleEnvs v2.0.0-beta.1
> 
> For stable v1.1.4 documentation, see: [v1.1.4 docs](https://github.com/vmintf/SimpleEnvs-Python/tree/v1.1.4/docs)

## 🚀 Why SimpleEnvs v2.0?

SimpleEnvs v2.0 is a **revolutionary upgrade** that delivers unprecedented performance and enterprise-grade security:

- 🏃‍♂️ **2-40x faster** loading performance (massive improvement!)
- 🔒 **Enterprise-grade security** with memory isolation and 51 attack vector protection
- ⚡ **Async optimization** with aiofiles integration
- 🎯 **Automatic type conversion** (int, bool, float)
- 🔍 **Smart directory scanning** with auto-discovery
- 💾 **Memory efficient** with optimized parsing
- 🐍 **Python 3.7-3.13** support (including latest Python!)
- 🔄 **100% python-dotenv compatible** API

## ⚡ Revolutionary Performance

**Breakthrough performance improvements in v2.0:**

| Variables | File Size | python-dotenv | SimpleEnvs v2.0 | **Speedup** |
|-----------|-----------|---------------|------------------|-------------|
| 10 vars | 482B | 1.96ms | **0.15ms** | **13.1x faster** ⚡ |
| 100 vars | 2.3KB | 10.59ms | **0.40ms** | **26.2x faster** ⚡ |
| 500 vars | 11KB | 55.24ms | **1.98ms** | **27.9x faster** ⚡ |
| 1000 vars | 22KB | 101.7ms | **4.97ms** | **20.5x faster** ⚡ |
| 5000 vars | 111KB | 632.8ms | **71.3ms** | **8.9x faster** ⚡ |

*Benchmarked on real hardware with comprehensive test suites*

### 🔒 Security Performance

Even our **secure mode** outperforms python-dotenv:

| Variables | SimpleEnvs Secure | python-dotenv | **Advantage** |
|-----------|-------------------|---------------|---------------|
| 100 vars | 0.77ms | 10.59ms | **13.8x faster** 🛡️ |
| 500 vars | 1.57ms | 55.24ms | **35.2x faster** 🛡️ |
| 1000 vars | 2.76ms | 101.7ms | **36.8x faster** 🛡️ |

*Memory-isolated security that's still faster than standard loading!*

## ⚡ Quick Example

```python
# Create .env file
echo "APP_NAME=MyApp\nDEBUG=true\nPORT=8080" > .env

# Load environment variables (just like python-dotenv!)
from simpleenvs import load_dotenv
load_dotenv()

# Access variables with automatic type conversion
import os
print(os.getenv('APP_NAME'))  # "MyApp"
print(os.getenv('DEBUG'))     # "True" (auto-converted!)
print(os.getenv('PORT'))      # "8080"
```

## 🛡️ Enterprise Security Mode

**NEW in v2.0:** Memory-isolated security that protects against 51 attack vectors:

```python
from simpleenvs import load_dotenv_secure, get_secure

# Load with maximum security (memory-isolated)
load_dotenv_secure()

# Access secure variables (NOT in os.environ!)
jwt_secret = get_secure('JWT_SECRET')
db_password = get_secure('DB_PASSWORD')

# Verify security isolation
import os
print(os.getenv('JWT_SECRET'))  # None - properly isolated! 🔒
```

### 🔍 Security Test Matrix

SimpleEnvs v2.0 has been tested against **51 security attack vectors**:

- ✅ **Path Traversal Protection** (8 attack patterns blocked)
- ✅ **Code Injection Defense** (7 injection patterns detected)
- ✅ **File Size Attack Prevention** (4 size limit scenarios)
- ✅ **Memory Security** (3 isolation mechanisms)
- ✅ **Input Validation** (13 validation checks)
- ✅ **Session Security** (6 access control tests)
- ✅ **Configuration Protection** (4 config attack vectors)
- ✅ **Edge Case Handling** (5 boundary conditions)

*100% security test pass rate with comprehensive coverage*

## 🚀 Smart Auto-Discovery

**Enhanced in v2.0:** Intelligent file discovery across your project:

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

# SimpleEnvs v2.0 (auto-discovery 🚀)
from simpleenvs import load_dotenv
load_dotenv()  # Finds the first .env file automatically!
```

## 🎯 Advanced Features

### Async Optimization

```python
import simpleenvs

# Async loading with aiofiles optimization
await simpleenvs.load('.env')
await simpleenvs.load_secure('.env')

# Or async one-liner
from simpleenvs import aload_dotenv
await aload_dotenv()
```

### Type-Safe Access

```python
import simpleenvs

simpleenvs.load_dotenv()

# Automatic type conversion
app_name = simpleenvs.get_str('APP_NAME', 'DefaultApp')  # str
debug = simpleenvs.get_bool('DEBUG', False)             # bool  
port = simpleenvs.get_int('PORT', 8080)                 # int
rate = simpleenvs.get_float('RATE', 1.0)               # float (NEW!)
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

## 🆚 SimpleEnvs v2.0 vs Competition

| Feature | python-dotenv | SimpleEnvs v2.0 |
|---------|---------------|-----------------|
| **Performance** | Baseline | **2-40x faster** ⚡ |
| **Memory Efficiency** | Standard | **Optimized parsing** 💾 |
| **Type Safety** | Manual casting | **Automatic conversion** 🎯 |
| **Security** | Basic | **Enterprise-grade** 🔒 |
| **Memory Isolation** | ❌ | **✅ Secure mode** |
| **Async Support** | ❌ | **✅ Full async/await** |
| **Auto-discovery** | ❌ | **✅ Smart scanning** |
| **Attack Protection** | ❌ | **✅ 51 vectors tested** |
| **Python 3.13** | ❌ | **✅ Latest support** |
| **API Compatibility** | ✅ | **✅ Drop-in replacement** |

### 📈 Performance Breakdown by Scale

| Variables | python-dotenv | SimpleEnvs v2.0 | **Improvement** |
|-----------|---------------|------------------|-----------------|
| Small (10) | 1.96ms | **0.15ms** | **13.1x faster** ⚡ |
| Medium (100) | 10.59ms | **0.40ms** | **26.2x faster** ⚡ |
| Large (1000) | 101.7ms | **4.97ms** | **20.5x faster** ⚡ |
| Enterprise (5000) | 632.8ms | **71.3ms** | **8.9x faster** ⚡ |

## 🔧 Migration Guide

### Instant Migration (Zero Changes!)

```python
# Before (python-dotenv)
from dotenv import load_dotenv
load_dotenv()

# After (SimpleEnvs v2.0) - Only change the import!
from simpleenvs import load_dotenv
load_dotenv()  # Same API, 2-40x faster! 🚀
```

### Enhanced Usage (Optional)

```python
# Take advantage of new features
from simpleenvs import load_dotenv_secure, get_secure

# For sensitive data
load_dotenv_secure()
api_key = get_secure('API_KEY')  # Memory-isolated

# For regular config
load_dotenv()
app_name = simpleenvs.get_str('APP_NAME')  # Type-safe
```

## 📚 Documentation

```{toctree}
:maxdepth: 2
:caption: Contents:

installation
quickstart
api-reference
security
```

## 🎯 Use Cases

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

## 🏆 Benchmarks

Run your own performance tests:

```bash
# Install with benchmark dependencies
pip install 'simpleenvs-python[benchmark]'

# Run comprehensive benchmark
python -m simpleenvs.benchmark

# Quick benchmark
python -m simpleenvs.benchmark --quick

# Include security benchmark
python -m simpleenvs.benchmark --secure
```

## 🔗 Links

- 📦 [PyPI Package](https://pypi.org/project/simpleenvs-python/)
- 🐛 [Issue Tracker](https://github.com/vmintf/SimpleEnvs-Python/issues)
- 💬 [Discussions](https://github.com/vmintf/SimpleEnvs-Python/discussions)
- 🔒 [Security Report](https://github.com/vmintf/SimpleEnvs-Python/security)
- 📧 [Contact](mailto:vmintf@gmail.com)

## 📄 License

MIT License - see [LICENSE](https://github.com/vmintf/SimpleEnvs-Python/blob/main/LICENSE) file for details.

---

**Ready to experience the future of .env loading?** Check out the [Installation Guide](installation.md)! 🎉

*SimpleEnvs v2.0 - Where performance meets security* 🚀🔒
