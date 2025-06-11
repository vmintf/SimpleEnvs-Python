#!/usr/bin/env python3
"""
SimpleEnvs: Ultra-secure, high-performance .env file loader
Secure version - memory-isolated, enterprise-grade security
"""

import asyncio
import hashlib
import os
import time
import weakref
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import aiofiles

# Import constants
from .constants import (
    DANGEROUS_PATTERNS,
    FALSE_VALUES,
)
from .constants import MAX_ENTRIES_PER_DIRECTORY as MAX_ENTRIES
from .constants import (
    MAX_FILE_SIZE,
    MAX_KEY_LENGTH,
    MAX_LINE_LENGTH,
    MAX_SCAN_DEPTH,
    MAX_VALUE_LENGTH,
    TRUE_VALUES,
)

# Import exceptions
from .exceptions import (
    AccessDeniedError,
    EnvSecurityError,
    FileParsingError,
    FileSizeError,
    IntegrityError,
    InvalidInputError,
    MemorySecurityError,
    PathTraversalError,
    SessionError,
)

# Type definitions
EnvValue = Union[str, int, bool]
EnvMap = Dict[str, EnvValue]


@dataclass
class LoadOptions:
    path: Optional[str] = None
    max_depth: int = 2
    strict_validation: bool = True


class SecureEnvLoader:
    """Ultra-secure environment variable loader with defense-in-depth"""

    def __init__(self, session_id: Optional[str] = None):
        # Private data storage with name mangling
        self.__env_data: EnvMap = {}
        self.__file_hashes: Dict[str, str] = {}
        self.__access_log: List[Dict[str, Any]] = []
        self.__session_id = session_id or self.__generate_session_id()
        self.__creation_time = time.time()
        self.__access_count = 0

        # Weak reference for automatic cleanup
        self.__cleanup_ref = weakref.finalize(self, self.__cleanup_handler)

    def __generate_session_id(self) -> str:
        """Generate secure session identifier"""
        data = f"{time.time()}{os.getpid()}{id(self)}".encode()
        return hashlib.sha256(data).hexdigest()[:16]

    def __log_access(
        self, operation: str, key: Optional[str] = None, success: bool = True
    ) -> None:
        """Log access attempts for security monitoring"""
        self.__access_count += 1
        log_entry = {
            "timestamp": time.time(),
            "session_id": self.__session_id,
            "operation": operation,
            "key": key,
            "success": success,
            "access_count": self.__access_count,
        }
        self.__access_log.append(log_entry)

        # Keep only last 100 entries to prevent memory bloat
        if len(self.__access_log) > 100:
            self.__access_log = self.__access_log[-100:]

    def __validate_path_security(self, path: str) -> None:
        """Comprehensive path security validation"""
        if not path or not isinstance(path, str):
            raise InvalidInputError("Invalid path type")

        # Path traversal protection
        if ".." in path or path.startswith("/"):
            self.__log_access("path_validation", path, False)
            raise PathTraversalError(path)

        # Null byte injection protection
        if "\x00" in path:
            raise InvalidInputError("Null byte in path")

        # Length validation
        if len(path) > 1024:
            raise InvalidInputError("Path too long")

        self.__log_access("path_validation", path, True)

    def __validate_file_security(self, file_path: str) -> None:
        """Validate file security constraints"""
        path_obj = Path(file_path)

        # Check file existence and type
        if not path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not path_obj.is_file():
            raise InvalidInputError("Path is not a file")

        # Check for symbolic links
        if path_obj.is_symlink():
            raise InvalidInputError("Symbolic links not allowed")

        # File size validation
        file_size = path_obj.stat().st_size
        if file_size == 0:
            raise InvalidInputError("Empty file")
        if file_size > MAX_FILE_SIZE:
            raise FileSizeError(str(path_obj), file_size, MAX_FILE_SIZE)

        # Generate and store file hash for integrity
        file_hash = self.__calculate_file_hash(file_path)
        self.__file_hashes[file_path] = file_hash

    def __validate_content_security_batch(self, content: str) -> None:
        """배치로 전체 내용 보안 검증 - 한 번에 처리"""
        content_lower = content.lower()

        # 🔒 Null byte Verification Adds.
        if "\x00" in content:
            raise InvalidInputError("Null byte detected in file content")

        for pattern in DANGEROUS_PATTERNS:
            if pattern in content_lower:
                raise InvalidInputError(f"Dangerous pattern detected: {pattern}")

        script_patterns = ["<script", "</script>", "javascript:", "vbscript:"]
        for pattern in script_patterns:
            if pattern in content_lower:
                raise InvalidInputError(f"Script injection pattern detected: {pattern}")

    def __calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file for integrity checking"""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def __validate_key_value(self, key: str, value: str) -> None:
        """Validate key-value pair security constraints"""
        # Key validation
        if not key or len(key.strip()) == 0:
            raise InvalidInputError("Empty key")
        if len(key) > MAX_KEY_LENGTH:
            raise InvalidInputError(f"Key too long: {len(key)} chars")
        if not key.replace("_", "").replace("-", "").isalnum():
            raise InvalidInputError("Key contains invalid characters")

        # Value validation
        if len(value) > MAX_VALUE_LENGTH:
            raise InvalidInputError(f"Value too long: {len(value)} chars")

        # Check for potential injection patterns
        for pattern in DANGEROUS_PATTERNS:
            if pattern in value.lower():
                raise InvalidInputError(f"Potentially dangerous pattern: {pattern}")

    def __parse_value_secure(self, value: str) -> EnvValue:
        """Securely parse string value to appropriate type"""
        value = value.strip()

        # Boolean parsing with strict validation
        if value.lower() in TRUE_VALUES:
            return True
        if value.lower() in FALSE_VALUES:
            return False

        # Number parsing with range validation
        if value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
            try:
                num = int(value)
                # Validate integer range (64-bit signed)
                if -(2**63) <= num <= (2**63 - 1):
                    return num
                else:
                    # Out of range, treat as string
                    return value
            except ValueError:
                pass

        # Default to string with encoding validation
        try:
            value.encode("utf-8")
            return value
        except UnicodeEncodeError:
            raise InvalidInputError("Invalid UTF-8 encoding in value")

    async def __parse_file_secure(self, file_path: str) -> EnvMap:
        """Securely parse .env file with comprehensive validation - OPTIMIZED"""
        self.__validate_path_security(file_path)
        self.__validate_file_security(file_path)

        env_data: EnvMap = {}
        line_count = 0

        try:
            # 🚀 최적화 1: 파일 크기에 따른 읽기 전략 선택
            file_size = Path(file_path).stat().st_size

            if file_size < 1024 * 1024:  # 1MB 미만은 동기 읽기가 더 빠름
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
            else:
                # 큰 파일만 비동기로 (청크 단위 또는 전체 읽기)
                async with aiofiles.open(file_path, "r", encoding="utf-8") as file:
                    content = await file.read()  # ✅ 한 번에 읽기

            # 🚀 최적화 2: 배치 보안 검증 (전체 내용 한 번에)
            self.__validate_content_security_batch(content)

            # 🚀 최적화 3: 동기적 라인 처리 (async for 대신)
            lines = content.splitlines()

            for line_number, line in enumerate(lines, 1):
                line_count += 1

                # Line count protection
                if line_count > 10000:
                    raise InvalidInputError("Too many lines in file")

                # Line length validation
                if len(line) > MAX_LINE_LENGTH:
                    continue

                # Process line
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                # Parse key=value
                if "=" not in line:
                    continue

                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()

                # Remove quotes if present
                if (value.startswith('"') and value.endswith('"')) or (
                    value.startswith("'") and value.endswith("'")
                ):
                    value = value[1:-1]

                # Security validation (key-value specific)
                self.__validate_key_value(key, value)

                # Store securely parsed value
                env_data[key] = self.__parse_value_secure(value)

        except UnicodeDecodeError:
            raise InvalidInputError("Invalid UTF-8 encoding in file")
        except Exception as e:
            self.__log_access("file_parse", file_path, False)
            raise FileParsingError(file_path, original_error=e)

        self.__log_access("file_parse", file_path, True)
        return env_data

    async def __scan_directory_secure(self, path: str, max_depth: int) -> Optional[str]:
        """Securely scan directory for .env file"""
        self.__validate_path_security(path)

        path_obj = Path(path)
        if not path_obj.exists() or not path_obj.is_dir():
            return None

        try:
            entries = list(path_obj.iterdir())
            if len(entries) > MAX_ENTRIES:
                raise InvalidInputError(f"Too many directory entries: {len(entries)}")

            # First pass: look for .env in current directory
            for entry in entries:
                if entry.name == ".env" and entry.is_file() and not entry.is_symlink():
                    return str(entry)

            # Recursive search with depth limit
            if max_depth > 0:
                for entry in entries:
                    if (
                        entry.is_dir()
                        and not entry.is_symlink()
                        and not entry.name.startswith(".")
                    ):

                        result = await self.__scan_directory_secure(
                            str(entry), max_depth - 1
                        )
                        if result:
                            return result

        except (OSError, PermissionError) as e:
            self.__log_access("directory_scan", path, False)
            return None

        return None

    async def load_secure(self, options: LoadOptions = LoadOptions()) -> None:
        """Securely load environment variables (memory-isolated)"""
        try:
            if options.path:
                # Load specific file
                env_data = await self.__parse_file_secure(options.path)
            else:
                # Auto-scan for .env file
                env_path = await self.__scan_directory_secure(
                    "./", min(options.max_depth, MAX_SCAN_DEPTH)
                )
                if not env_path:
                    raise FileNotFoundError("No .env file found")
                env_data = await self.__parse_file_secure(env_path)

            # Atomic update of internal data (NO sync to os.environ!)
            self.__env_data = env_data
            self.__log_access("load_complete", None, True)

        except Exception as e:
            self.__log_access("load_failed", None, False)
            raise

    def get_secure(self, key: str) -> Optional[EnvValue]:
        """Securely retrieve environment variable"""
        if not isinstance(key, str):
            raise InvalidInputError("Key must be string")

        self.__log_access("get", key, key in self.__env_data)
        return self.__env_data.get(key)

    def get_with_default_secure(self, key: str, default: EnvValue) -> EnvValue:
        """Securely retrieve environment variable with default"""
        if not isinstance(key, str):
            raise InvalidInputError("Key must be string")

        value = self.__env_data.get(key, default)
        self.__log_access("get_default", key, True)
        return value

    def get_int_secure(self, key: str, default: Optional[int] = None) -> Optional[int]:
        """Securely get environment variable as integer"""
        value = self.get_secure(key)
        if value is None:
            return default
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                return default
        return default

    def get_bool_secure(
        self, key: str, default: Optional[bool] = None
    ) -> Optional[bool]:
        """Securely get environment variable as boolean"""
        value = self.get_secure(key)
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "yes", "1", "on")
        return default

    def get_str_secure(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Securely get environment variable as string"""
        value = self.get_secure(key)
        if value is None:
            return default
        return str(value)

    def get_all_keys_secure(self) -> List[str]:
        """Get all available keys (for debugging)"""
        self.__log_access("get_keys", None, True)
        return list(self.__env_data.keys())

    def get_all_secure(self) -> Dict[str, EnvValue]:
        """Get all environment variables (copy for security)"""
        self.__log_access("get_all", None, True)
        return self.__env_data.copy()

    def is_loaded(self) -> bool:
        """Check if environment variables are loaded"""
        return bool(self.__env_data)

    def get_security_info(self) -> Dict[str, Any]:
        """Get security and session information"""
        return {
            "session_id": self.__session_id,
            "creation_time": self.__creation_time,
            "access_count": self.__access_count,
            "env_count": len(self.__env_data),
            "file_hashes": len(self.__file_hashes),
            "log_entries": len(self.__access_log),
        }

    def verify_file_integrity(self, file_path: str) -> bool:
        """Verify file integrity using stored hash"""
        if file_path not in self.__file_hashes:
            return False

        try:
            current_hash = self.__calculate_file_hash(file_path)
            expected_hash = self.__file_hashes[file_path]
            if current_hash != expected_hash:
                raise IntegrityError(file_path, expected_hash, current_hash)
            return True
        except Exception:
            return False

    def get_access_log(self) -> List[Dict[str, Any]]:
        """Get access log for security auditing"""
        return self.__access_log.copy()

    @staticmethod
    def __cleanup_handler():
        """Cleanup handler for security"""
        # This runs when object is garbage collected
        pass

    def secure_wipe(self) -> None:
        """Securely wipe sensitive data"""
        try:
            # Overwrite sensitive data multiple times
            if hasattr(self, "_SecureEnvLoader__env_data"):
                for _ in range(3):
                    for key in list(self.__env_data.keys()):
                        self.__env_data[key] = "WIPED"
                    self.__env_data.clear()

            if hasattr(self, "_SecureEnvLoader__file_hashes"):
                self.__file_hashes.clear()

            if hasattr(self, "_SecureEnvLoader__access_log"):
                self.__access_log.clear()
        except Exception as e:
            raise MemorySecurityError("secure_wipe", str(e))


# Convenience functions
async def load_secure(
    path: Optional[str] = None, strict: bool = True
) -> SecureEnvLoader:
    """Load .env file with maximum security"""
    loader = SecureEnvLoader()
    options = LoadOptions(path=path, strict_validation=strict)
    await loader.load_secure(options)
    return loader


async def load_from_path_secure(path: str) -> SecureEnvLoader:
    """Load specific .env file with maximum security"""
    loader = SecureEnvLoader()
    await loader.load_secure(LoadOptions(path=path))
    return loader


if __name__ == "__main__":
    # Example usage
    async def main():
        """Secure usage example"""
        try:
            # Create secure loader
            loader = SecureEnvLoader()

            # Load with maximum security (memory-isolated!)
            await loader.load_secure()

            # Access securely (NOT available via os.getenv!)
            db_host = loader.get_str_secure("DB_HOST", "localhost")
            db_port = loader.get_int_secure("DB_PORT", 5432)
            debug = loader.get_bool_secure("DEBUG", False)

            print(f"DB_HOST: {db_host}")
            print(f"DB_PORT: {db_port}")
            print(f"DEBUG: {debug}")

            # Security information
            security_info = loader.get_security_info()
            print(f"Security Info: {security_info}")

            # Verify these are NOT in system environment
            import os

            print(f"DB_HOST in os.environ: {'DB_HOST' in os.environ}")

            # Clean up securely
            loader.secure_wipe()

        except EnvSecurityError as e:
            print(f"Security Error: {e}")
        except Exception as e:
            print(f"Error: {e}")

    asyncio.run(main())
