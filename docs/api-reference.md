# API Reference

Complete reference for all SimpleEnvs functions and classes.

## Table of Contents

- [Loading Functions](#loading-functions)
- [Simple API (System Environment)](#simple-api-system-environment)
- [Secure API (Memory-Isolated)](#secure-api-memory-isolated)
- [Type-Safe Getters](#type-safe-getters)
- [Utility Functions](#utility-functions)
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

## Type-Safe Getters

All getter functions support type conversion with validation:

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

### `get_all_secure_loaders()`

Get all SecureEnvLoader instances in memory.

**Returns:** List[SecureEnvLoader]

**Example:**
```python
loaders = simpleenvs.get_all_secure_loaders()
print(f"Found {len(loaders)} secure loaders in memory")
```

---

## Cross-Module Access

SimpleEnvs provides automatic cross-module access to secure environment variables through memory introspection.

### How It Works

When you load secure environment variables in one module, other modules can automatically access the same data without re-loading:

```python
# main.py - Load secrets once
import simpleenvs
await simpleenvs.load_secure('.env.production')

# utils.py - Automatic access  
import simpleenvs
api_key = simpleenvs.get_secure('API_KEY')  # Finds loader from main.py!
```

### Memory Discovery

The system uses `gc.get_objects()` to find existing SecureEnvLoader instances:

```python
def _find_secure_loader_in_memory() -> Optional[SecureEnvLoader]:
    """Find existing SecureEnvLoader instance in memory"""
    try:
        for obj in gc.get_objects():
            if (isinstance(obj, SecureEnvLoader) 
                and hasattr(obj, "_SecureEnvLoader__env_data")
                and obj._SecureEnvLoader__env_data):
                return obj
    except Exception:
        pass
    return None
```

### Security Properties

Cross-module access maintains all security guarantees:
- Memory isolation preserved
- Access logging continues
- Session tracking maintained
- No data in `os.environ`

### Usage Patterns

#### Web Application Startup
```python
# app.py
async def startup():
    await simpleenvs.load_secure()

# Any other module
database_url = simpleenvs.get_secure('DATABASE_URL')  # Works automatically
```

#### Service Layer Pattern
```python
# config.py - Central configuration
await simpleenvs.load_secure('.env.secrets')

# services/auth.py
jwt_secret = simpleenvs.get_secure('JWT_SECRET')

# services/database.py  
db_password = simpleenvs.get_secure('DB_PASSWORD')
```

#### Module Testing
```python
# test_utils.py
def test_api_client():
    # Test can access secrets loaded in conftest.py
    api_key = simpleenvs.get_secure('TEST_API_KEY')
    assert api_key is not None
```

### Fallback Behavior

If no SecureEnvLoader is found in memory, functions return default values:

```python
# No secure loader loaded yet
result = simpleenvs.get_secure('API_KEY', 'default')
print(result)  # 'default'

# After loading in another module
await simpleenvs.load_secure()
result = simpleenvs.get_secure('API_KEY', 'default') 
print(result)  # Actual API key value
```

---

## Utility Functions

### `get_all_keys()`

Get all available environment variable keys.

**Returns:** List[str]

**Example:**
```python
keys = simpleenvs.get_all_keys()
print(f"Available variables: {keys}")
```

### `clear()`

Clear all loaded environment data.

**Returns:** None

**Example:**
```python
simpleenvs.clear()  # Clean up all data
```

### `get_info()`

Get information about loaded environments.

**Returns:** Dict[str, Any]

**Example:**
```python
info = simpleenvs.get_info()
print(f"Version: {info['version']}")
print(f"Simple loaded: {info['simple_loaded']}")
print(f"Secure loaded: {info['secure_loaded']}")
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

##### `get(key)`

Get environment variable from local data.

##### `get_int(key, default=None)`

Get environment variable as integer.

##### `get_bool(key, default=None)`

Get environment variable as boolean.

##### `get_str(key, default=None)`

Get environment variable as string.

##### `is_loaded()`

Check if environment variables are loaded.

##### `clear()`

Clear all loaded environment variables.

**Example:**
```python
from simpleenvs import SimpleEnvLoader

loader = SimpleEnvLoader()
await loader.load('.env')
value = loader.get('KEY')
```

### `SecureEnvLoader`

Ultra-secure environment variable loader with defense-in-depth.

#### Methods

##### `__init__(session_id=None)`

Initialize secure loader with optional session ID.

##### `async load_secure(options=LoadOptions())`

Securely load environment variables (memory-isolated).

##### `get_secure(key)`

Securely retrieve environment variable.

##### `get_int_secure(key, default=None)`

Securely get environment variable as integer.

##### `get_bool_secure(key, default=None)`

Securely get environment variable as boolean.

##### `get_str_secure(key, default=None)`

Securely get environment variable as string.

##### `get_security_info()`

Get security and session information.

##### `verify_file_integrity(file_path)`

Verify file integrity using stored hash.

##### `secure_wipe()`

Securely wipe sensitive data.

**Example:**
```python
from simpleenvs import SecureEnvLoader

loader = SecureEnvLoader()
await loader.load_secure()
secret = loader.get_secure('SECRET_KEY')
```

### `LoadOptions`

Configuration options for secure loading.

#### Attributes

- `path` (str, optional): File path
- `max_depth` (int): Maximum search depth
- `strict_validation` (bool): Enable strict validation

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

### `SimpleEnvsError`

Base exception for all SimpleEnvs errors.

### `EnvSecurityError`

Base security exception for SecureEnvLoader.

### `PathTraversalError`

Path traversal attack detected.

### `FileSizeError`

File size exceeds security limits.

### `InvalidInputError`

Input validation failed.

### `AccessDeniedError`

Access to internal methods denied.

### `FileParsingError`

Error occurred during file parsing.

### `EnvNotLoadedError`

Environment variables not loaded yet.

### `KeyNotFoundError`

Environment variable key not found.

### `TypeConversionError`

Type conversion failed.

### `ConfigurationError`

Configuration or setup error.

### `IntegrityError`

File integrity check failed.

### `SessionError`

Session-related security error.

### `MemorySecurityError`

Memory security violation.

**Example:**
```python
try:
    simpleenvs.load_dotenv('nonexistent.env')
except simpleenvs.FileNotFoundError:
    print("File not found")
except simpleenvs.SimpleEnvsError as e:
    print(f"Error: {e}")
```

---

## Constants

### Version Information

- `__version__`: Library version string
- `VERSION`: Same as __version__
- `API_VERSION`: API version

### Security Limits

- `MAX_FILE_SIZE`: 10MB maximum file size
- `MAX_KEY_LENGTH`: 128 characters maximum key length
- `MAX_VALUE_LENGTH`: 1024 characters maximum value length
- `MAX_SCAN_DEPTH`: 3 levels maximum search depth

### Environment Types

- `get_environment_type()`: Returns current environment type
- Supported: "development", "production", "testing", "staging"

**Example:**
```python
import simpleenvs
print(f"Version: {simpleenvs.__version__}")
print(f"Environment: {simpleenvs.get_environment_type()}")
```

---

## Type Definitions

```python
from typing import Union, Dict, List, Optional

EnvValue = Union[str, int, bool]
EnvMap = Dict[str, EnvValue]
```

---

## Need Help?

- 🐛 [Report issues](https://github.com/vmintf/SimpleEnvs-Python/issues)
- 💬 [Join discussions](https://github.com/vmintf/SimpleEnvs-Python/discussions)
- 📧 [Contact support](mailto:vmintf@gmail.com)
- 📚 [Full documentation](https://github.com/vmintf/SimpleEnvs-Python)

---

**Next:** Learn about [Security Features](security.md) for enterprise-grade protection! 🔒