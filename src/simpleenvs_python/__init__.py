#!/usr/bin/env python3
"""
SimpleEnvs: Ultra-secure, high-performance .env file loader

Simple to use, enterprise-grade security and performance.
Provides both simple (system-level) and secure (memory-isolated) environment loading.

Usage:
    # Simple system-level loading
    import simpleenvs
    await simpleenvs.load()
    db_host = simpleenvs.get("DB_HOST")  # or os.getenv("DB_HOST")

    # Secure memory-isolated loading
    await simpleenvs.load_secure()
    db_host = simpleenvs.get_secure("DB_HOST")  # NOT in os.environ!

    # Direct class usage
    from simpleenvs import SimpleEnvLoader, SecureEnvLoader
    loader = SimpleEnvLoader()
    await loader.load()
"""

import gc
import os
from typing import Any, Dict, List, Optional, Union

from .constants import LIBRARY_NAME, VERSION, get_environment_type
from .exceptions import *
from .secure import SecureEnvLoader
from .secure import load_secure as _load_secure_func

# Import all classes and exceptions
from .simple import SimpleEnvLoader, load_env, load_env_sync

# Type definitions
EnvValue = Union[str, int, bool]

# Version information
__version__ = VERSION
__author__ = "SimpleEnvs Team"
__license__ = "MIT"
__description__ = "Ultra-secure, high-performance .env file loader"

# Global instances for convenience API
_simple_loader: Optional[SimpleEnvLoader] = None
_secure_loader: Optional[SecureEnvLoader] = None


# =============================================================================
# SIMPLE API (System-level environment variables)
# =============================================================================


async def load(path: Optional[str] = None, max_depth: int = 2) -> None:
    """
    Load environment variables using SimpleEnvLoader (syncs to os.environ)

    Args:
        path: Specific .env file path, or None for auto-discovery
        max_depth: Maximum directory depth to search for .env files

    Usage:
        await simpleenvs.load()
        db_host = simpleenvs.get("DB_HOST")  # or os.getenv("DB_HOST")
    """
    global _simple_loader
    if _simple_loader is None:
        _simple_loader = SimpleEnvLoader()

    await _simple_loader.load(path, max_depth)


def load_sync(path: Optional[str] = None, max_depth: int = 2) -> None:
    """
    Load environment variables synchronously using SimpleEnvLoader

    Args:
        path: Specific .env file path, or None for auto-discovery
        max_depth: Maximum directory depth to search for .env files

    Usage:
        simpleenvs.load_sync()
        db_host = simpleenvs.get("DB_HOST")  # or os.getenv("DB_HOST")
    """
    global _simple_loader
    if _simple_loader is None:
        _simple_loader = SimpleEnvLoader()

    _simple_loader.load_sync(path, max_depth)


def get(key: str, default: Optional[EnvValue] = None) -> Optional[EnvValue]:
    """
    Get environment variable (from system environment after loading)

    Args:
        key: Environment variable name
        default: Default value if not found

    Returns:
        Environment variable value or default

    Note:
        This uses os.getenv() since SimpleEnvLoader syncs to system environment
    """
    return os.getenv(key, default)


def get_int(key: str, default: Optional[int] = None) -> Optional[int]:
    """Get environment variable as integer"""
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def get_bool(key: str, default: Optional[bool] = None) -> Optional[bool]:
    """Get environment variable as boolean"""
    value = os.getenv(key)
    if value is None:
        return default
    return value.lower() in ("true", "yes", "1", "on", "enable", "enabled")


def get_str(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get environment variable as string"""
    return os.getenv(key, default)


def is_loaded() -> bool:
    """Check if simple environment is loaded"""
    return _simple_loader is not None and _simple_loader.is_loaded()


# =============================================================================
# SECURE API (Memory-isolated environment variables)
# =============================================================================


async def load_secure(
    path: Optional[str] = None, strict: bool = True, max_depth: int = 2
) -> None:
    """
    Load environment variables using SecureEnvLoader (memory-isolated)

    Args:
        path: Specific .env file path, or None for auto-discovery
        strict: Enable strict security validation
        max_depth: Maximum directory depth to search for .env files

    Usage:
        await simpleenvs.load_secure()
        db_host = simpleenvs.get_secure("DB_HOST")  # NOT in os.environ!
    """
    global _secure_loader
    if _secure_loader is None:
        _secure_loader = SecureEnvLoader()

    from .secure import LoadOptions

    options = LoadOptions(path=path, max_depth=max_depth, strict_validation=strict)
    await _secure_loader.load_secure(options)


def get_secure(key: str, default: Optional[EnvValue] = None) -> Optional[EnvValue]:
    """
    Get secure environment variable (memory-isolated, NOT in os.environ)

    Args:
        key: Environment variable name
        default: Default value if not found

    Returns:
        Environment variable value or default

    Note:
        This accesses memory-isolated data, not system environment
    """
    if _secure_loader is None:
        # Try to find existing SecureEnvLoader in memory
        found_loader = _find_secure_loader_in_memory()
        if found_loader:
            return found_loader.get_secure(key) or default
        return default

    return _secure_loader.get_secure(key) or default


def get_int_secure(key: str, default: Optional[int] = None) -> Optional[int]:
    """Get secure environment variable as integer"""
    if _secure_loader is None:
        found_loader = _find_secure_loader_in_memory()
        if found_loader:
            return found_loader.get_int_secure(key, default)
        return default

    return _secure_loader.get_int_secure(key, default)


def get_bool_secure(key: str, default: Optional[bool] = None) -> Optional[bool]:
    """Get secure environment variable as boolean"""
    if _secure_loader is None:
        found_loader = _find_secure_loader_in_memory()
        if found_loader:
            return found_loader.get_bool_secure(key, default)
        return default

    return _secure_loader.get_bool_secure(key, default)


def get_str_secure(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get secure environment variable as string"""
    if _secure_loader is None:
        found_loader = _find_secure_loader_in_memory()
        if found_loader:
            return found_loader.get_str_secure(key, default)
        return default

    return _secure_loader.get_str_secure(key, default)


def is_loaded_secure() -> bool:
    """Check if secure environment is loaded"""
    if _secure_loader is not None:
        return _secure_loader.is_loaded()

    # Check memory for existing loaded instances
    found_loader = _find_secure_loader_in_memory()
    return found_loader is not None and found_loader.is_loaded()


def get_security_info() -> Optional[Dict[str, Any]]:
    """Get security information from secure loader"""
    if _secure_loader is not None:
        return _secure_loader.get_security_info()

    found_loader = _find_secure_loader_in_memory()
    if found_loader:
        return found_loader.get_security_info()

    return None


# =============================================================================
# MEMORY INTROSPECTION (for finding existing SecureEnvLoader instances)
# =============================================================================


def _find_secure_loader_in_memory() -> Optional[SecureEnvLoader]:
    """
    Find existing SecureEnvLoader instance in memory
    This enables access to secure environment variables from anywhere in the codebase
    """
    try:
        for obj in gc.get_objects():
            if (
                isinstance(obj, SecureEnvLoader)
                and hasattr(obj, "_SecureEnvLoader__env_data")
                and obj._SecureEnvLoader__env_data
            ):  # Has loaded data
                return obj
    except Exception:
        pass  # Silently fail if introspection not possible

    return None


def get_all_secure_loaders() -> List[SecureEnvLoader]:
    """Get all SecureEnvLoader instances in memory (for debugging)"""
    loaders = []
    try:
        for obj in gc.get_objects():
            if isinstance(obj, SecureEnvLoader):
                loaders.append(obj)
    except Exception:
        pass

    return loaders


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def get_all_keys() -> List[str]:
    """Get all available environment variable keys"""
    keys = set()

    # From simple loader (system environment)
    if _simple_loader and _simple_loader.is_loaded():
        keys.update(_simple_loader.keys())

    # From secure loader (memory-isolated)
    if _secure_loader and _secure_loader.is_loaded():
        keys.update(_secure_loader.get_all_keys_secure())
    else:
        # Check memory for other secure loaders
        found_loader = _find_secure_loader_in_memory()
        if found_loader:
            keys.update(found_loader.get_all_keys_secure())

    return sorted(list(keys))


def clear() -> None:
    """Clear all loaded environment data"""
    global _simple_loader, _secure_loader

    if _simple_loader:
        _simple_loader.clear()

    if _secure_loader:
        _secure_loader.secure_wipe()


def get_info() -> Dict[str, Any]:
    """Get information about loaded environments"""
    return {
        "version": __version__,
        "environment_type": get_environment_type(),
        "simple_loaded": is_loaded(),
        "secure_loaded": is_loaded_secure(),
        "total_keys": len(get_all_keys()),
        "simple_loader": _simple_loader is not None,
        "secure_loader": _secure_loader is not None,
        "secure_loaders_in_memory": len(get_all_secure_loaders()),
    }


# =============================================================================
# BACKWARDS COMPATIBILITY & CONVENIENCE
# =============================================================================

# Alias for common usage patterns
load_env_simple = load
load_env_secure = load_secure


# Super convenient one-liner functions (like python-dotenv)
def load_dotenv(path: Optional[str] = None) -> None:
    """
    One-liner to load .env file synchronously (python-dotenv compatibility)

    Args:
        path: Path to .env file, or None for auto-discovery

    Usage:
        from simpleenvs import load_dotenv
        load_dotenv()  # Just like python-dotenv!
    """
    global _simple_loader
    if _simple_loader is None:
        _simple_loader = SimpleEnvLoader()

    _simple_loader.load_sync(path)


async def aload_dotenv(path: Optional[str] = None) -> None:
    """
    One-liner to load .env file asynchronously

    Args:
        path: Path to .env file, or None for auto-discovery

    Usage:
        from simpleenvs import aload_dotenv
        await aload_dotenv()  # Async version
    """
    await load(path)


def load_dotenv_secure(path: Optional[str] = None, strict: bool = True) -> None:
    """
    One-liner to load .env file with maximum security (memory-isolated)

    Args:
        path: Path to .env file, or None for auto-discovery
        strict: Enable strict security validation

    Usage:
        from simpleenvs import load_dotenv_secure
        load_dotenv_secure()  # Maximum security!
    """
    import asyncio

    asyncio.run(load_secure(path, strict))


# Class exports
__all__ = [
    # Classes
    "SimpleEnvLoader",
    "SecureEnvLoader",
    # Simple API (system-level)
    "load",
    "load_sync",
    "get",
    "get_int",
    "get_bool",
    "get_str",
    "is_loaded",
    # Secure API (memory-isolated)
    "load_secure",
    "get_secure",
    "get_int_secure",
    "get_bool_secure",
    "get_str_secure",
    "is_loaded_secure",
    "get_security_info",
    # Utilities
    "get_all_keys",
    "clear",
    "get_info",
    # Convenience one-liners (python-dotenv style)
    "load_dotenv",  # Sync version
    "aload_dotenv",  # Async version
    "load_dotenv_secure",  # Secure version
    # Backwards compatibility
    "load_env_simple",
    "load_env_secure",
    # Exceptions (re-exported)
    "SimpleEnvsError",
    "EnvSecurityError",
    "PathTraversalError",
    "FileSizeError",
    "InvalidInputError",
    "AccessDeniedError",
    "FileParsingError",
    "EnvNotLoadedError",
    "KeyNotFoundError",
    "TypeConversionError",
    "ConfigurationError",
    "IntegrityError",
    "SessionError",
    "MemorySecurityError",
    # Constants
    "__version__",
]


# =============================================================================
# EXAMPLES AND DOCUMENTATION
# =============================================================================


def _example_usage():
    """Example usage patterns (for documentation)"""

    # Simple usage (most common)
    async def simple_example():
        # Load and use immediately
        await load()
        db_host = get("DB_HOST", "localhost")
        db_port = get_int("DB_PORT", 5432)
        debug = get_bool("DEBUG", False)

        # Also available via os.getenv since it syncs to system
        import os

        api_key = os.getenv("API_KEY")

    # Secure usage (enterprise/production)
    async def secure_example():
        # Load with maximum security (memory-isolated)
        await load_secure()
        jwt_secret = get_secure("JWT_SECRET")

        # NOT available via os.getenv (memory-isolated!)
        import os

        assert os.getenv("JWT_SECRET") is None  # Not in system environment

    # Mixed usage
    async def mixed_example():
        # Simple for non-sensitive config
        await load()
        app_name = get("APP_NAME", "MyApp")

        # Secure for sensitive data
        await load_secure()
        database_password = get_secure("DATABASE_PASSWORD")

    # Direct class usage
    async def direct_example():
        # When you need more control
        simple_loader = SimpleEnvLoader()
        await simple_loader.load("/path/to/.env")

        secure_loader = SecureEnvLoader()
        await secure_loader.load_secure()

        # Access security info
        security_info = secure_loader.get_security_info()


if __name__ == "__main__":
    # Display library information
    print(f"{LIBRARY_NAME} v{__version__}")
    print(__description__)
    print(f"Environment: {get_environment_type()}")
    print(f"Simple loaded: {is_loaded()}")
    print(f"Secure loaded: {is_loaded_secure()}")
    print(f"Available keys: {len(get_all_keys())}")

    # Example quick test
    import asyncio

    async def quick_test():
        try:
            print("\nTesting simple loading...")
            await load()
            print(f"Simple loaded: {is_loaded()}")
        except FileNotFoundError:
            print("No .env file found for testing")
        except Exception as e:
            print(f"Error: {e}")

    asyncio.run(quick_test())
