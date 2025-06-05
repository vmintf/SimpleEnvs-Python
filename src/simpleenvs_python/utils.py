#!/usr/bin/env python3
"""
SimpleEnvs: Common utility functions
Shared utilities for parsing, validation, and file operations
"""

import hashlib
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from .constants import (
    DANGEROUS_PATTERNS,
    DEFAULT_ENCODING,
    ENV_FILE_PATTERNS,
    EXCLUDED_DIRECTORIES,
    FALSE_VALUES,
    PATH_TRAVERSAL_PATTERNS,
    SUPPORTED_ENCODINGS,
    TRUE_VALUES,
)
from .exceptions import (
    FileParsingError,
    InvalidInputError,
    PathTraversalError,
    TypeConversionError,
)

# Type definitions
EnvValue = Union[str, int, bool]
EnvMap = Dict[str, EnvValue]


# =============================================================================
# VALUE PARSING UTILITIES
# =============================================================================


def parse_env_value(value: str, strict: bool = False) -> EnvValue:
    """
    Parse environment variable value to appropriate type

    Args:
        value: String value to parse
        strict: Enable strict parsing with validation

    Returns:
        Parsed value as string, int, or bool

    Raises:
        TypeConversionError: If strict mode and conversion fails
        InvalidInputError: If value contains dangerous patterns in strict mode
    """
    if not isinstance(value, str):
        if strict:
            raise TypeConversionError("value", value, "string")
        return str(value)

    value = value.strip()

    # Empty value handling
    if not value:
        return ""

    # Security check in strict mode
    if strict:
        validate_value_security(value)

    # Boolean parsing
    if value.lower() in TRUE_VALUES:
        return True
    if value.lower() in FALSE_VALUES:
        return False

    # Integer parsing with range validation
    if value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
        try:
            num = int(value)
            # Validate integer range (64-bit signed)
            if -(2**63) <= num <= (2**63 - 1):
                return num
            elif strict:
                raise TypeConversionError("value", value, "64-bit integer")
            else:
                return value  # Return as string if out of range
        except ValueError:
            if strict:
                raise TypeConversionError("value", value, "integer")

    # Float parsing (optional)
    if "." in value:
        try:
            return float(value)
        except ValueError:
            if strict:
                raise TypeConversionError("value", value, "float")

    # Default to string with encoding validation
    try:
        value.encode("utf-8")
        return value
    except UnicodeEncodeError:
        if strict:
            raise InvalidInputError("Invalid UTF-8 encoding in value", value)
        return value


def normalize_boolean(value: Any) -> bool:
    """
    Normalize various value types to boolean

    Args:
        value: Value to convert to boolean

    Returns:
        Boolean representation of the value
    """
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value.lower() in TRUE_VALUES

    if isinstance(value, (int, float)):
        return bool(value)

    return bool(value)


def normalize_env_key(key: str) -> str:
    """
    Normalize environment variable key to standard format

    Args:
        key: Environment variable key

    Returns:
        Normalized key (uppercase, underscores)
    """
    if not isinstance(key, str):
        raise InvalidInputError("Key must be string", str(key))

    # Convert to uppercase and replace hyphens with underscores
    normalized = key.upper().replace("-", "_")

    # Remove invalid characters
    normalized = re.sub(r"[^A-Z0-9_]", "", normalized)

    # Ensure it starts with a letter or underscore
    if normalized and not normalized[0].isalpha() and normalized[0] != "_":
        normalized = "_" + normalized

    return normalized


# =============================================================================
# SECURITY VALIDATION UTILITIES
# =============================================================================


def validate_value_security(value: str) -> None:
    """
    Validate value for security issues

    Args:
        value: Value to validate

    Raises:
        InvalidInputError: If dangerous patterns detected
    """
    if not isinstance(value, str):
        return

    value_lower = value.lower()

    # Check for dangerous patterns
    for pattern in DANGEROUS_PATTERNS:
        if pattern in value_lower:
            raise InvalidInputError(f"Dangerous pattern detected: {pattern}", value)

    # Check for script injection patterns
    script_patterns = ["<script", "</script>", "javascript:", "vbscript:"]
    for pattern in script_patterns:
        if pattern in value_lower:
            raise InvalidInputError(
                f"Script injection pattern detected: {pattern}", value
            )


def validate_path_security(path: str) -> None:
    """
    Validate path for security issues

    Args:
        path: File path to validate

    Raises:
        PathTraversalError: If path traversal detected
        InvalidInputError: If path is invalid
    """
    if not path or not isinstance(path, str):
        raise InvalidInputError("Invalid path type", str(path))

    # Check for path traversal patterns
    for pattern in PATH_TRAVERSAL_PATTERNS:
        if pattern in path:
            raise PathTraversalError(path)

    # Additional checks
    if "\x00" in path:
        raise InvalidInputError("Null byte in path", path)

    if len(path) > 1024:
        raise InvalidInputError("Path too long", path)


def validate_key_format(key: str, strict: bool = True) -> None:
    """
    Validate environment variable key format

    Args:
        key: Environment variable key
        strict: Enable strict validation

    Raises:
        InvalidInputError: If key format is invalid
    """
    if not key or not isinstance(key, str):
        raise InvalidInputError("Key must be non-empty string", str(key))

    if strict:
        # Strict validation: alphanumeric + underscore + hyphen only
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", key):
            raise InvalidInputError("Key contains invalid characters", key)
    else:
        # Relaxed validation: just check for dangerous characters
        if any(char in key for char in ["=", "\n", "\r", "\x00"]):
            raise InvalidInputError("Key contains dangerous characters", key)


# =============================================================================
# FILE OPERATIONS UTILITIES
# =============================================================================


def find_env_files(start_path: str = "./", max_depth: int = 3) -> List[str]:
    """
    Find all .env files in directory tree

    Args:
        start_path: Starting directory path
        max_depth: Maximum search depth

    Returns:
        List of found .env file paths
    """
    found_files = []

    def _search_directory(path: Path, depth: int) -> None:
        if depth <= 0:
            return

        if not path.exists() or not path.is_dir():
            return

        try:
            # Check for env files in current directory
            for pattern in ENV_FILE_PATTERNS:
                env_file = path / pattern
                if (
                    env_file.exists()
                    and env_file.is_file()
                    and not env_file.is_symlink()
                ):
                    found_files.append(str(env_file))

            # Search subdirectories
            for item in path.iterdir():
                if (
                    item.is_dir()
                    and not item.is_symlink()
                    and item.name not in EXCLUDED_DIRECTORIES
                ):
                    _search_directory(item, depth - 1)

        except (OSError, PermissionError):
            pass  # Skip inaccessible directories

    _search_directory(Path(start_path), max_depth)
    return found_files


def detect_file_encoding(file_path: str) -> str:
    """
    Detect file encoding by trying multiple encodings

    Args:
        file_path: Path to file

    Returns:
        Detected encoding name

    Raises:
        FileParsingError: If no supported encoding works
    """
    for encoding in SUPPORTED_ENCODINGS:
        try:
            with open(file_path, "r", encoding=encoding) as f:
                # Try to read a chunk to verify encoding
                f.read(1024)
            return encoding
        except UnicodeDecodeError:
            continue
        except Exception:
            break

    raise FileParsingError(
        file_path, original_error=Exception("No supported encoding found")
    )


def calculate_file_hash(file_path: str, algorithm: str = "sha256") -> str:
    """
    Calculate file hash for integrity checking

    Args:
        file_path: Path to file
        algorithm: Hash algorithm ('sha256', 'md5', etc.)

    Returns:
        Hexadecimal hash string

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If unsupported algorithm
    """
    if not Path(file_path).exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        hasher = hashlib.new(algorithm)
    except ValueError:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)

    return hasher.hexdigest()


def safe_file_read(file_path: str, max_size: int = 10 * 1024 * 1024) -> Tuple[str, str]:
    """
    Safely read file with size limit and encoding detection

    Args:
        file_path: Path to file
        max_size: Maximum file size in bytes

    Returns:
        Tuple of (file_content, detected_encoding)

    Raises:
        FileParsingError: If file too large or can't be read
    """
    path_obj = Path(file_path)

    if not path_obj.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    file_size = path_obj.stat().st_size
    if file_size > max_size:
        raise FileParsingError(
            file_path,
            original_error=Exception(
                f"File too large: {file_size} bytes (max: {max_size})"
            ),
        )

    encoding = detect_file_encoding(file_path)

    try:
        with open(file_path, "r", encoding=encoding) as f:
            content = f.read()
        return content, encoding
    except Exception as e:
        raise FileParsingError(file_path, original_error=e)


# =============================================================================
# PARSING UTILITIES
# =============================================================================


def parse_env_line(
    line: str, line_number: int = 0, strict: bool = False
) -> Optional[Tuple[str, EnvValue]]:
    """
    Parse a single line from .env file

    Args:
        line: Line to parse
        line_number: Line number for error reporting
        strict: Enable strict validation

    Returns:
        Tuple of (key, value) or None if line should be skipped

    Raises:
        FileParsingError: If parsing fails in strict mode
    """
    line = line.strip()

    # Skip empty lines and comments
    if not line or line.startswith("#"):
        return None

    # Must contain '='
    if "=" not in line:
        if strict:
            raise FileParsingError(
                "", line_number, Exception("Line missing '=' separator")
            )
        return None

    # Split on first '='
    key, _, value = line.partition("=")
    key = key.strip()
    value = value.strip()

    if not key:
        if strict:
            raise FileParsingError("", line_number, Exception("Empty key"))
        return None

    # Validate key format
    if strict:
        validate_key_format(key, strict=True)

    # Remove quotes if present
    if len(value) >= 2:
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]

    # Parse value
    try:
        parsed_value = parse_env_value(value, strict=strict)
        return key, parsed_value
    except (TypeConversionError, InvalidInputError) as e:
        if strict:
            raise FileParsingError("", line_number, e)
        # In non-strict mode, return as string
        return key, value


def parse_env_content(content: str, strict: bool = False) -> EnvMap:
    """
    Parse complete .env file content

    Args:
        content: File content to parse
        strict: Enable strict validation

    Returns:
        Dictionary of environment variables

    Raises:
        FileParsingError: If parsing fails
    """
    env_data = {}

    for line_number, line in enumerate(content.splitlines(), 1):
        try:
            result = parse_env_line(line, line_number, strict)
            if result:
                key, value = result
                env_data[key] = value
        except FileParsingError:
            raise  # Re-raise with line number info
        except Exception as e:
            if strict:
                raise FileParsingError("", line_number, e)
            # In non-strict mode, skip problematic lines
            continue

    return env_data


# =============================================================================
# DEBUGGING AND INTROSPECTION UTILITIES
# =============================================================================


def get_env_info(env_data: EnvMap) -> Dict[str, Any]:
    """
    Get information about environment data

    Args:
        env_data: Environment variables dictionary

    Returns:
        Information dictionary
    """
    if not env_data:
        return {"count": 0, "types": {}, "keys": []}

    type_counts = {}
    for value in env_data.values():
        type_name = type(value).__name__
        type_counts[type_name] = type_counts.get(type_name, 0) + 1

    return {
        "count": len(env_data),
        "types": type_counts,
        "keys": sorted(env_data.keys()),
        "max_key_length": max(len(k) for k in env_data.keys()) if env_data else 0,
        "max_value_length": (
            max(len(str(v)) for v in env_data.values()) if env_data else 0
        ),
    }


def format_env_summary(env_data: EnvMap, show_values: bool = False) -> str:
    """
    Format environment data summary for display

    Args:
        env_data: Environment variables dictionary
        show_values: Whether to show actual values (security risk!)

    Returns:
        Formatted summary string
    """
    info = get_env_info(env_data)

    lines = [
        f"Environment Variables Summary:",
        f"  Total: {info['count']} variables",
        f"  Types: {info['types']}",
        f"  Keys: {', '.join(info['keys'][:10])}"
        + ("..." if len(info["keys"]) > 10 else ""),
    ]

    if show_values and env_data:
        lines.append("\nValues:")
        for key, value in sorted(env_data.items()):
            lines.append(f"  {key} = {repr(value)}")

    return "\n".join(lines)


def validate_env_completeness(env_data: EnvMap, required_keys: List[str]) -> List[str]:
    """
    Validate that all required environment variables are present

    Args:
        env_data: Environment variables dictionary
        required_keys: List of required keys

    Returns:
        List of missing keys
    """
    return [key for key in required_keys if key not in env_data]


# =============================================================================
# EXPORT UTILITIES
# =============================================================================


def export_to_shell_format(env_data: EnvMap, quote_values: bool = True) -> str:
    """
    Export environment variables to shell format

    Args:
        env_data: Environment variables dictionary
        quote_values: Whether to quote values

    Returns:
        Shell export statements
    """
    lines = []
    for key, value in sorted(env_data.items()):
        if quote_values:
            lines.append(f'export {key}="{value}"')
        else:
            lines.append(f"export {key}={value}")
    return "\n".join(lines)


def export_to_env_format(env_data: EnvMap) -> str:
    """
    Export environment variables back to .env format

    Args:
        env_data: Environment variables dictionary

    Returns:
        .env format string
    """
    lines = []
    for key, value in sorted(env_data.items()):
        if isinstance(value, str) and (" " in value or '"' in value or "'" in value):
            # Quote values with spaces or quotes
            escaped_value = value.replace('"', '\\"')
            lines.append(f'{key}="{escaped_value}"')
        else:
            lines.append(f"{key}={value}")
    return "\n".join(lines)


if __name__ == "__main__":
    # Example usage and testing
    test_content = """
# Test .env file
APP_NAME=SimpleEnvs
DEBUG=true
PORT=8080
DATABASE_URL="postgresql://user:pass@localhost/db"
"""

    print("Testing utility functions:")

    # Test parsing
    env_data = parse_env_content(test_content, strict=False)
    print(f"Parsed: {env_data}")

    # Test info
    info = get_env_info(env_data)
    print(f"Info: {info}")

    # Test summary
    summary = format_env_summary(env_data, show_values=True)
    print(f"Summary:\n{summary}")

    # Test export
    shell_export = export_to_shell_format(env_data)
    print(f"Shell export:\n{shell_export}")
