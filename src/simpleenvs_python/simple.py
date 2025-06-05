#!/usr/bin/env python3
"""
SimpleEnvs: Simple and fast .env file loader
Simple version - syncs to system environment variables
"""

import asyncio
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import aiofiles

# Import constants
from .constants import (
    DEFAULT_ENCODING,
    ENV_FILE_PATTERNS,
    EXCLUDED_DIRECTORIES,
    FALSE_VALUES,
    MAX_SCAN_DEPTH,
    SUPPORTED_ENCODINGS,
    TRUE_VALUES,
)

# Import exceptions
from .exceptions import (
    EnvNotLoadedError,
    FileParsingError,
    InvalidInputError,
    KeyNotFoundError,
    SimpleEnvsError,
    TypeConversionError,
)

# Import utilities
from .utils import (
    detect_file_encoding,
    find_env_files,
    parse_env_content,
    parse_env_value,
    safe_file_read,
    validate_key_format,
)

# Type definitions
EnvValue = Union[str, int, bool]
EnvMap = Dict[str, EnvValue]


class SimpleEnvLoader:
    """Simple, fast .env loader that syncs to system environment variables"""

    def __init__(self):
        """Initialize simple loader"""
        self.env_data: EnvMap = {}

    def _parse_value(self, value: str) -> EnvValue:
        """Parse string value to appropriate type (deprecated - use utils.parse_env_value)"""
        # Use utils function for consistency
        return parse_env_value(value, strict=False)

    async def _find_env_file(
        self, start_path: str = "./", max_depth: int = 2
    ) -> Optional[str]:
        """Find .env file in directory tree"""
        if not isinstance(start_path, str):
            raise InvalidInputError("start_path must be string", start_path)

        # Use utils function but return first match only
        found_files = find_env_files(start_path, max_depth)
        return found_files[0] if found_files else None

    def _find_env_file_sync(
        self, start_path: str = "./", max_depth: int = 2
    ) -> Optional[str]:
        """Find .env file in directory tree synchronously"""
        if not isinstance(start_path, str):
            raise InvalidInputError("start_path must be string", start_path)

        # Use utils function but return first match only
        found_files = find_env_files(start_path, max_depth)
        return found_files[0] if found_files else None

    async def _parse_file(self, file_path: str) -> EnvMap:
        """Parse .env file asynchronously"""
        if not isinstance(file_path, str):
            raise InvalidInputError("file_path must be string", file_path)

        try:
            # Use utils for safe file reading
            content, encoding = safe_file_read(file_path)

            # Use utils for parsing
            return parse_env_content(content, strict=False)

        except (FileNotFoundError, FileParsingError):
            raise  # Re-raise these specific exceptions
        except Exception as e:
            raise FileParsingError(file_path, original_error=e)

    def _parse_file_sync(self, file_path: str) -> EnvMap:
        """Parse .env file synchronously"""
        if not isinstance(file_path, str):
            raise InvalidInputError("file_path must be string", file_path)

        try:
            # Use utils for safe file reading
            content, encoding = safe_file_read(file_path)

            # Use utils for parsing
            return parse_env_content(content, strict=False)

        except (FileNotFoundError, FileParsingError):
            raise  # Re-raise these specific exceptions
        except Exception as e:
            raise FileParsingError(file_path, original_error=e)

    async def load(self, path: Optional[str] = None, max_depth: int = 2) -> None:
        """Load environment variables from .env file and sync to system"""
        # Validate max_depth
        if max_depth < 0 or max_depth > MAX_SCAN_DEPTH:
            raise InvalidInputError(
                f"max_depth must be between 0 and {MAX_SCAN_DEPTH}", str(max_depth)
            )

        try:
            if path:
                # Load specific file
                if not Path(path).exists():
                    raise FileNotFoundError(f"File not found: {path}")
                env_data = await self._parse_file(path)
            else:
                # Auto-find .env file
                env_path = await self._find_env_file(max_depth=max_depth)
                if not env_path:
                    raise FileNotFoundError("No .env file found in directory tree")
                env_data = await self._parse_file(env_path)

            # Update local data
            self.env_data = env_data

            # Sync to system environment variables
            for key, value in env_data.items():
                os.environ[key] = str(value)

        except (FileNotFoundError, FileParsingError, InvalidInputError):
            raise  # Re-raise these specific exceptions
        except Exception as e:
            raise SimpleEnvsError(
                f"Failed to load environment: {e}",
                {"path": path, "max_depth": max_depth},
            )

    def load_sync(self, path: Optional[str] = None, max_depth: int = 2) -> None:
        """Load environment variables synchronously and sync to system"""
        # Validate max_depth
        if max_depth < 0 or max_depth > MAX_SCAN_DEPTH:
            raise InvalidInputError(
                f"max_depth must be between 0 and {MAX_SCAN_DEPTH}", str(max_depth)
            )

        try:
            if path:
                # Load specific file
                if not Path(path).exists():
                    raise FileNotFoundError(f"File not found: {path}")
                env_data = self._parse_file_sync(path)
            else:
                # Auto-find .env file
                env_path = self._find_env_file_sync(max_depth=max_depth)
                if not env_path:
                    raise FileNotFoundError("No .env file found in directory tree")
                env_data = self._parse_file_sync(env_path)

            # Update local data
            self.env_data = env_data

            # Sync to system environment variables
            for key, value in env_data.items():
                os.environ[key] = str(value)

        except (FileNotFoundError, FileParsingError, InvalidInputError):
            raise  # Re-raise these specific exceptions
        except Exception as e:
            raise SimpleEnvsError(
                f"Failed to load environment: {e}",
                {"path": path, "max_depth": max_depth},
            )

    def get(self, key: str) -> Optional[EnvValue]:
        """Get environment variable from local data"""
        if not isinstance(key, str):
            raise InvalidInputError("Key must be string", key)

        if not self.env_data:
            raise EnvNotLoadedError("get operation")

        return self.env_data.get(key)

    def get_with_default(self, key: str, default: EnvValue) -> EnvValue:
        """Get environment variable with default value from local data"""
        if not isinstance(key, str):
            raise InvalidInputError("Key must be string", key)

        if not self.env_data:
            raise EnvNotLoadedError("get_with_default operation")

        return self.env_data.get(key, default)

    def get_int(self, key: str, default: Optional[int] = None) -> Optional[int]:
        """Get environment variable as integer"""
        if not isinstance(key, str):
            raise InvalidInputError("Key must be string", key)

        if not self.env_data:
            raise EnvNotLoadedError("get_int operation")

        value = self.env_data.get(key, default)
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                raise TypeConversionError(key, value, "integer")
        return default

    def get_bool(self, key: str, default: Optional[bool] = None) -> Optional[bool]:
        """Get environment variable as boolean"""
        if not isinstance(key, str):
            raise InvalidInputError("Key must be string", key)

        if not self.env_data:
            raise EnvNotLoadedError("get_bool operation")

        value = self.env_data.get(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            # Use utils function for consistent boolean parsing
            from .utils import normalize_boolean

            try:
                return normalize_boolean(value)
            except Exception:
                raise TypeConversionError(key, value, "boolean")
        return default

    def get_str(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get environment variable as string"""
        if not isinstance(key, str):
            raise InvalidInputError("Key must be string", key)

        if not self.env_data:
            raise EnvNotLoadedError("get_str operation")

        value = self.env_data.get(key, default)
        return str(value) if value is not None else default

    def get_all(self) -> Dict[str, EnvValue]:
        """Get all environment variables"""
        if not self.env_data:
            raise EnvNotLoadedError("get_all operation")

        return self.env_data.copy()

    def keys(self) -> List[str]:
        """Get all available keys"""
        if not self.env_data:
            raise EnvNotLoadedError("keys operation")

        return list(self.env_data.keys())

    def clear(self) -> None:
        """Clear all loaded environment variables (local only, doesn't affect os.environ)"""
        self.env_data.clear()

    def is_loaded(self) -> bool:
        """Check if environment variables are loaded"""
        return bool(self.env_data)


# Convenience functions
async def load_env(path: Optional[str] = None) -> SimpleEnvLoader:
    """Convenience function to load .env file asynchronously"""
    loader = SimpleEnvLoader()
    await loader.load(path)
    return loader


def load_env_sync(path: Optional[str] = None) -> SimpleEnvLoader:
    """Convenience function to load .env file synchronously"""
    loader = SimpleEnvLoader()
    loader.load_sync(path)
    return loader


if __name__ == "__main__":
    # Example usage
    async def main():
        try:
            # Async loading
            loader = SimpleEnvLoader()
            await loader.load()

            # After loading, variables are available both ways:
            # 1. Through loader methods
            db_host = loader.get_str("DB_HOST", "localhost")

            # 2. Through system environment (since we sync)
            import os

            db_port = int(os.getenv("DB_PORT", "5432"))
            debug = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes", "on")

            print(f"DB_HOST: {db_host}")
            print(f"DB_PORT: {db_port}")
            print(f"DEBUG: {debug}")

        except FileNotFoundError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    asyncio.run(main())
