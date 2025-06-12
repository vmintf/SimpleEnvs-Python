# SimpleEnvs API Reference

Complete reference for all SimpleEnvs functions and classes with latest updates.

## Table of Contents

- [Loading Functions](#loading-functions)
- [Simple API (System Environment)](#simple-api-system-environment)
- [Secure API (Memory-Isolated)](#secure-api-memory-isolated)
- [SecureLoaderManager (NEW!)](#secureloadermanager-new)
- [Type-Safe Getters](#type-safe-getters)
- [Utility Functions](#utility-functions)
- [Performance & Benchmarking](#performance--benchmarking)
- [Classes](#classes)
- [Exceptions](#exceptions)
- [Constants](#constants)

---

## Loading Functions

### `load_dotenv(path=None)`

One-liner to load .env file synchronously (python-dotenv compatible).

**Parameters:**
- `path` (str, optional): Path to .env file, or None for auto-discovery

**Returns:** None

**Example:**
```python
from simpleenvs import load_dotenv
load_dotenv()  # Auto-discover .env file
load_dotenv('.env.production')  # Specific file
```

### `aload_dotenv(path=None)`

One-liner to load .env file asynchronously.

**Parameters:**
- `path` (str, optional): Path to .env file, or None for auto-discovery

**Returns:** None

**Example:**
```python
from simpleenvs import aload_dotenv
await aload_dotenv()
```

### `load_dotenv_secure(path=None, strict=True)`

One-liner to load .env file with maximum security (memory-isolated).

**Parameters:**
- `path` (str, optional): Path to .env file, or None for auto-discovery
- `strict` (bool): Enable strict security validation

**Returns:** None

**Example:**
```python
from simpleenvs import load_dotenv_secure
load_dotenv_secure()  # Maximum security!
```

---

## Simple API (System Environment)

Functions that sync environment variables to `os.environ`.

### `load(path=None, max_depth=2)`

Load environment variables asynchronously using SimpleEnvLoader.

**Parameters:**
- `path` (str, optional): Specific .env file path, or None for auto-discovery
- `max_depth` (int): Maximum directory depth to search for .env files

**Returns:** None

**Example:**
```python
import simpleenvs
await simpleenvs.load()
await simpleenvs.load('.env.production', max_depth=1)
```

### `load_sync(path=None, max_depth=2)`

Load environment variables synchronously using SimpleEnvLoader.

**Parameters:**
- `path` (str, optional): Specific .env file path, or None for auto-discovery
- `max_depth` (int): Maximum directory depth to search for .env files

**Returns:** None

**Example:**
```python
import simpleenvs
simpleenvs.load_sync()
```

### `get(key, default=None)`

Get environment variable from system environment.

**Parameters:**
- `key` (str): Environment variable name
- `default` (EnvValue, optional): Default value if not found

**Returns:** Optional[EnvValue]

**Note:** Uses `os.getenv()` since SimpleEnvLoader syncs to system environment.

**Example:**
```python
db_host = simpleenvs.get('DB_HOST', 'localhost')
```

### `get_int(key, default=None)`

Get environment variable as integer.

**Parameters:**
- `key` (str): Environment variable name
- `default` (int, optional): Default value if not found

**Returns:** Optional[int]

**Example:**
```python
port = simpleenvs.get_int('PORT', 8080)
```

### `get_bool(key, default=None)`

Get environment variable as boolean.

**Parameters:**
- `key` (str): Environment variable name
- `default` (bool, optional): Default value if not found

**Returns:** Optional[bool]

**Note:** Recognizes: "true", "yes", "1", "on", "enable", "enabled" as True

**Example:**
```python
debug = simpleenvs.get_bool('DEBUG', False)
```

### `get_str(key, default=None)`

Get environment variable as string.

**Parameters:**
- `key` (str): Environment variable name
- `default` (str, optional): Default value if not found

**Returns:** Optional[str]

**Example:**
```python
app_name = simpleenvs.get_str('APP_NAME', 'MyApp')
```

### `is_loaded()`

Check if simple environment is loaded.

**Returns:** bool

**Example:**
```python
if simpleenvs.is_loaded():
    print("Environment loaded successfully")
```

---

## Secure API (Memory-Isolated)

Functions that keep environment variables in memory, **NOT** in `os.environ`.

### `load_secure(path=None, strict=True, max_depth=2)`

Load environment variables using SecureEnvLoader (memory-isolated).

**Parameters:**
- `path` (str, optional): Specific .env file path, or None for auto-discovery
- `strict` (bool): Enable strict security validation
- `max_depth` (int): Maximum directory depth to search for .env files

**Returns:** None

**Example:**
```python
await simpleenvs.load_secure()
await simpleenvs.load_secure('.env.secrets', strict=True)
```

### `get_secure(key, default=None)`

Get secure environment variable (memory-isolated, NOT in os.environ).

**Parameters:**
- `key` (str): Environment variable name
- `default` (EnvValue, optional): Default value if not found

**Returns:** Optional[EnvValue]

**Note:** Uses SecureLoaderManager for cross-module access

**Example:**
```python
api_key = simpleenvs.get_secure('API_KEY')
```

### `get_int_secure(key, default=None)`

Get secure environment variable as integer.

**Parameters:**
- `key` (str): Environment variable name
- `default` (int, optional): Default value if not found

**Returns:** Optional[int]

**Example:**
```python
timeout = simpleenvs.get_int_secure('TIMEOUT', 30)
```

### `get_bool_secure(key, default=None)`

Get secure environment variable as boolean.

**Parameters:**
- `key` (str): Environment variable name
- `default` (bool, optional): Default value if not found

**Returns:** Optional[bool]

**Example:**
```python
secure_mode = simpleenvs.get_bool_secure('SECURE_MODE', True)
```

### `get_str_secure(key, default=None)`

Get secure environment variable as string.

**Parameters:**
- `key` (str): Environment variable name
- `default` (str, optional): Default value if not found

**Returns:** Optional[str]

**Example:**
```python
jwt_secret = simpleenvs.get_str_secure('JWT_SECRET')
```

### `is_loaded_secure()`

Check if secure environment is loaded.

**Returns:** bool

**Example:**
```python
if simpleenvs.is_loaded_secure():
    print("Secure environment loaded")
```

### `get_security_info()`

Get security information from secure loader.

**Returns:** Optional[Dict[str, Any]]

**Example:**
```python
info = simpleenvs.get_security_info()
print(f"Session ID: {info['session_id']}")
print(f"Access count: {info['access_count']}")
```

---

## SecureLoaderManager (NEW!)

**🆕 Enhanced cross-module access with pythonic interface**

The SecureLoaderManager provides intelligent management of SecureEnvLoader instances across your application with magic method support.

### `get_all_secure_loaders()`

Get all SecureEnvLoader instances in memory.

**Returns:** List[SecureEnvLoader]

**Example:**
```python
loaders = simpleenvs.get_all_secure_loaders()
print(f"Found {len(loaders)} secure loaders in memory")
```

### Magic Methods Support

The manager supports pythonic access patterns:

#### Length and Boolean Operations
```python
import simpleenvs

# Check if any secure loaders exist
if simpleenvs._secure_manager:
    print("Secure environment available")

# Get count of loaders in memory
loader_count = len(simpleenvs._secure_manager)
print(f"Active loaders: {loader_count}")
```

#### Dictionary-like Access
```python
# Direct key access (uses active loader)
secret = simpleenvs._secure_manager['SECRET_KEY']

# Equivalent to:
secret = simpleenvs.get_secure('SECRET_KEY')
```

#### Iteration Support
```python
# Iterate over all loaders
for loader in simpleenvs._secure_manager:
    info = loader.get_security_info()
    print(f"Loader session: {info['session_id']}")
```

### Cross-Module Access

Enhanced automatic discovery across modules:

```python
# main.py - Load secrets once
import simpleenvs
await simpleenvs.load_secure('.env.production')

# utils.py - Automatic access anywhere!
import simpleenvs
api_key = simpleenvs.get_secure('API_KEY')  # Works automatically!
```

### Memory Management

The manager intelligently handles:
- **Priority Resolution**: Global loader → Memory introspection → None
- **Automatic Cleanup**: Weak references prevent memory leaks
- **Session Tracking**: Multiple loaders with unique session IDs

---

## Type-Safe Getters

All getter functions support automatic type conversion with validation:

### Boolean Values

**True values:** "true", "yes", "1", "on", "enable", "enabled", "active", "ok", "y", "t"  
**False values:** "false", "no", "0", "off", "disable", "disabled", "inactive", "n", "f", "null", "none", ""

### Integer Values

- Supports positive and negative integers
- Range: -2^63 to 2^63-1 (64-bit signed)
- Out-of-range values remain as strings

### String Values

- All values can be converted to strings
- UTF-8 encoding validation in strict mode

### Performance Optimizations

Type conversion is now optimized with:
- **Batch processing** for large .env files
- **Caching** for repeated access
- **Early validation** during file parsing

---

## Utility Functions

### `get_all_keys()`

Get all available environment variable keys from both simple and secure loaders.

**Returns:** List[str]

**Example:**
```python
keys = simpleenvs.get_all_keys()
print(f"Available variables: {keys}")
```

### `clear()`

Clear all loaded environment data and secure wipe sensitive information.

**Returns:** None

**Note:** Now includes automatic SecureLoaderManager cleanup

**Example:**
```python
simpleenvs.clear()  # Clean up all data + secure wipe
```

### `get_info()`

Get comprehensive information about loaded environments.

**Returns:** Dict[str, Any]

**Enhanced with new fields:**
- `secure_loaders_in_memory`: Count of SecureEnvLoader instances
- `manager_status`: SecureLoaderManager status

**Example:**
```python
info = simpleenvs.get_info()
print(f"Version: {info['version']}")
print(f"Simple loaded: {info['simple_loaded']}")
print(f"Secure loaded: {info['secure_loaded']}")
print(f"Secure loaders in memory: {info['secure_loaders_in_memory']}")
```

---

## Performance & Benchmarking

**🚀 New performance monitoring and benchmarking tools**

### Built-in Benchmarking

SimpleEnvs includes comprehensive benchmarking tools:

```python
# Run built-in benchmark
python -m simpleenvs.benchmark

# Quick benchmark (3 rounds)
python -m simpleenvs.benchmark --quick

# Include Secure API benchmarking
python -m simpleenvs.benchmark --secure

# Test specific variable count
python -m simpleenvs.benchmark --size 1000
```

### Performance Monitoring

Monitor your application's .env loading performance:

```python
import time
import simpleenvs

# Measure loading time
start = time.perf_counter()
await simpleenvs.load_secure('large_config.env')
load_time = (time.perf_counter() - start) * 1000

print(f"Secure loading took: {load_time:.2f}ms")
```

### Security Performance Analysis

The secure API includes performance monitoring:

```python
# Get security info with performance metrics
info = simpleenvs.get_security_info()
print(f"Access count: {info['access_count']}")
print(f"Creation time: {info['creation_time']}")

# Access log for performance analysis
access_log = simpleenvs.get_all_secure_loaders()[0].get_access_log()
for entry in access_log[-5:]:  # Last 5 accesses
    print(f"{entry['operation']}: {entry['timestamp']}")
```

---

## Classes

### `SimpleEnvLoader`

Simple, fast .env loader that syncs to system environment variables.

#### Methods

##### `__init__()`

Initialize simple loader.

##### `async load(path=None, max_depth=2)`

Load environment variables from .env file and sync to system.

##### `load_sync(path=None, max_depth=2)`

Load environment variables synchronously and sync to system.

##### `get(key)`, `get_int(key, default=None)`, `get_bool(key, default=None)`, `get_str(key, default=None)`

Type-safe getters for environment variables.

##### `is_loaded()`, `clear()`, `keys()`, `get_all()`

Status and utility methods.

**Example:**
```python
from simpleenvs import SimpleEnvLoader

loader = SimpleEnvLoader()
await loader.load('.env')
value = loader.get('KEY')
```

### `SecureEnvLoader`

Ultra-secure environment variable loader with defense-in-depth and enhanced performance.

#### Enhanced Features

- **Batch Security Validation**: Optimized content scanning
- **Intelligent File Reading**: Size-based sync/async strategy
- **Memory Optimization**: Reduced parsing overhead
- **Session Tracking**: Detailed access logging

#### Methods

##### `__init__(session_id=None)`

Initialize secure loader with optional session ID.

##### `async load_secure(options=LoadOptions())`

Securely load environment variables with enhanced performance.

**New optimizations:**
- Files < 1MB: Synchronous reading (faster)
- Files > 1MB: Asynchronous reading (non-blocking)
- Batch security validation for better performance

##### `get_secure(key)`, `get_int_secure(key, default=None)`, etc.

Enhanced type-safe getters with performance monitoring.

##### `get_security_info()`

Get comprehensive security and performance information.

##### `verify_file_integrity(file_path)`, `secure_wipe()`

Security methods for integrity checking and data cleanup.

**Example:**
```python
from simpleenvs import SecureEnvLoader

loader = SecureEnvLoader(session_id="prod-001")
await loader.load_secure()
secret = loader.get_secure('SECRET_KEY')

# Performance monitoring
info = loader.get_security_info()
print(f"Access count: {info['access_count']}")
```

### `SecureLoaderManager` (NEW!)

Intelligent manager for SecureEnvLoader instances with pythonic interface.

#### Key Features

- **Automatic Discovery**: Finds loaders across modules
- **Priority Resolution**: Global → Memory → None
- **Magic Methods**: Pythonic `len()`, `bool()`, iteration
- **Memory Safety**: Weak references prevent leaks

#### Methods

##### `get_active_loader()`

Get the currently active SecureEnvLoader instance.

##### `get_all_loaders()`

Get all SecureEnvLoader instances in memory.

##### Magic Methods

- `__len__()`: Number of loaders in memory
- `__bool__()`: True if active loader exists
- `__iter__()`: Iterate over all loaders
- `__getitem__(key)`: Direct key access
- `__contains__(loader)`: Check if loader in memory

**Example:**
```python
from simpleenvs import SecureLoaderManager

manager = SecureLoaderManager()

if manager:  # __bool__
    print(f"Found {len(manager)} loaders")  # __len__
    
    secret = manager['SECRET_KEY']  # __getitem__
    
    for loader in manager:  # __iter__
        print(f"Session: {loader.get_security_info()['session_id']}")
```

### `LoadOptions`

Configuration options for secure loading with enhanced validation.

#### Attributes

- `path` (str, optional): File path
- `max_depth` (int): Maximum search depth  
- `strict_validation` (bool): Enable strict validation

**Enhanced validation includes:**
- Batch content security scanning
- Optimized path traversal detection
- Performance-aware file size limits

**Example:**
```python
from simpleenvs.secure import LoadOptions

options = LoadOptions(
    path='.env.production',
    max_depth=1,
    strict_validation=True
)
await loader.load_secure(options)
```

---

## Exceptions

All exceptions remain the same with enhanced error reporting:

### Core Exceptions

- `SimpleEnvsError`: Base exception for all SimpleEnvs errors
- `EnvSecurityError`: Base security exception
- `PathTraversalError`: Path traversal attack detected
- `FileSizeError`: File size exceeds security limits
- `InvalidInputError`: Input validation failed
- `AccessDeniedError`: Access to internal methods denied

### Parsing & Loading Exceptions

- `FileParsingError`: Error during file parsing (enhanced with line numbers)
- `EnvNotLoadedError`: Environment variables not loaded yet
- `KeyNotFoundError`: Environment variable key not found
- `TypeConversionError`: Type conversion failed

### Security & System Exceptions

- `ConfigurationError`: Configuration or setup error
- `IntegrityError`: File integrity check failed
- `SessionError`: Session-related security error
- `MemorySecurityError`: Memory security violation

**Enhanced Error Handling:**
```python
try:
    await simpleenvs.load_secure('config.env')
except simpleenvs.FileSizeError as e:
    print(f"File too large: {e.size} bytes (max: {e.max_size})")
except simpleenvs.PathTraversalError as e:
    print(f"Security violation: {e.attempted_path}")
except simpleenvs.SimpleEnvsError as e:
    print(f"General error: {e}")
```

---

## Constants

### Version Information

- `__version__`: Library version string (currently 1.1.4)
- `VERSION`: Same as __version__
- `API_VERSION`: API version

### Security Limits (Enhanced)

- `MAX_FILE_SIZE`: 10MB maximum file size
- `MAX_KEY_LENGTH`: 128 characters maximum key length
- `MAX_VALUE_LENGTH`: 1024 characters maximum value length
- `MAX_SCAN_DEPTH`: 3 levels maximum search depth
- `MAX_ENTRIES_PER_DIRECTORY`: 10,000 entries per directory
- `MAX_ACCESS_LOG_ENTRIES`: 100 access log entries (memory management)

### Performance Constants (NEW!)

- `READ_BUFFER_SIZE`: 8KB buffer for file reading
- `HASH_BUFFER_SIZE`: 4KB buffer for integrity hashing
- `CACHE_TTL`: 300 seconds cache timeout
- `FILE_READ_TIMEOUT`: 30 seconds file read timeout

### Environment Types

- `get_environment_type()`: Returns current environment type
- Supported: "development", "production", "testing", "staging"

**Example:**
```python
import simpleenvs
print(f"Version: {simpleenvs.__version__}")
print(f"Environment: {simpleenvs.get_environment_type()}")
print(f"Max file size: {simpleenvs.MAX_FILE_SIZE}")
```

---

## Migration Guide

### From v1.1.4 to v2.0.0

**✅ Fully Backward Compatible** - No breaking changes!

**New Features:**
```python
# NEW: SecureLoaderManager with magic methods
if simpleenvs._secure_manager:
    secret = simpleenvs._secure_manager['SECRET_KEY']

# NEW: Enhanced performance monitoring
info = simpleenvs.get_info()
loader_count = info['secure_loaders_in_memory']

# NEW: Built-in benchmarking
python -m simpleenvs.benchmark --secure --quick
```

**Performance Improvements:**
- 15-25% faster secure loading for large files
- Batch security validation
- Optimized memory introspection
- Enhanced cross-module access

---

## Best Practices (Updated)

### 1. Use Manager-Based Access

```python
# ✅ Recommended: Let manager handle discovery
import simpleenvs
await simpleenvs.load_secure()
secret = simpleenvs.get_secure('SECRET_KEY')  # Auto-discovery!

# ❌ Avoid: Manual loader management
loader = SecureEnvLoader()
await loader.load_secure()
secret = loader.get_secure('SECRET_KEY')
```

### 2. Monitor Performance

```python
# ✅ Monitor large file loading
info = simpleenvs.get_security_info()
if info and info['access_count'] > 1000:
    print("High access count - consider caching")

# ✅ Use built-in benchmarking
# python -m simpleenvs.benchmark --size 500 --secure
```

### 3. Environment-Specific Configuration

```python
# ✅ Leverage environment detection
import simpleenvs

env_type = simpleenvs.get_environment_type()
if env_type == 'production':
    await simpleenvs.load_secure(strict=True)  # Max security
else:
    await simpleenvs.load()  # Development flexibility
```

---

## Type Definitions

```python
from typing import Union, Dict, List, Optional

EnvValue = Union[str, int, bool]
EnvMap = Dict[str, EnvValue]

# New manager type
SecureLoaderManager = simpleenvs.manager.SecureLoaderManager
```

---

## Need Help?

- 🐛 [Report issues](https://github.com/vmintf/SimpleEnvs-Python/issues)
- 💬 [Join discussions](https://github.com/vmintf/SimpleEnvs-Python/discussions)
- 📧 [Contact support](mailto:vmintf@gmail.com)
- 📚 [Full documentation](https://github.com/vmintf/SimpleEnvs-Python)
- 🏃‍♂️ [Performance benchmarks](https://github.com/vmintf/SimpleEnvs-Python/tree/main/src/simpleenvs/benchmark.py)

---

**What's Next?** 
- 🔒 Learn about [Security Features](security.md) for enterprise-grade protection
- ⚡ Explore [Performance Guide](performance.md) for optimization tips
- 🏗️ Check out [Best Practices](best-practices.md) for production patterns

*Updated for SimpleEnvs v1.1.4 with SecureLoaderManager and performance enhancements* 🚀