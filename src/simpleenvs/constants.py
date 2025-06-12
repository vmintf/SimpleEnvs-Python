#!/usr/bin/env python3
"""
SimpleEnvs: Configuration constants and security limits
"""

import os
from typing import List, Set, Tuple

# =============================================================================
# SECURITY LIMITS
# =============================================================================

# File and input size limits
MAX_KEY_LENGTH = 128
MAX_VALUE_LENGTH = 1024
MAX_LINE_LENGTH = 4096
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_ENTRIES_PER_DIRECTORY = 10000
MAX_SCAN_DEPTH = 3
MAX_LINES_PER_FILE = 10000

# Memory and performance limits
MAX_ACCESS_LOG_ENTRIES = 100
MAX_FILE_HASH_CACHE = 50
MAX_SESSION_LIFETIME = 3600  # 1 hour in seconds
MAX_CONCURRENT_LOADS = 10

# Parsing limits
MAX_VARIABLE_COUNT = 1000
MAX_NESTING_DEPTH = 5
MAX_RECURSION_DEPTH = 10

# =============================================================================
# SECURITY PATTERNS
# =============================================================================

# Dangerous patterns to detect in values
DANGEROUS_PATTERNS: Set[str] = {
    "$(",
    "`",
    "${",
    "<!--",
    "<script",
    "</script>",
    "<iframe",
    "javascript:",
    "data:",
    "vbscript:",
    "onload=",
    "onerror=",
    "eval(",
    "exec(",
    "__import__",
    "subprocess",
    "os.system",
    "shell=True",
}

# Suspicious file extensions
SUSPICIOUS_EXTENSIONS: Set[str] = {
    ".exe",
    ".bat",
    ".cmd",
    ".sh",
    ".ps1",
    ".vbs",
    ".js",
    ".jar",
    ".class",
    ".py",
    ".pl",
    ".rb",
    ".php",
}

# Path traversal patterns
PATH_TRAVERSAL_PATTERNS: Set[str] = {
    "..",
    "/./",
    "\\..\\",
    "%2e%2e",
    "%252e%252e",
    "..%2f",
    "..%5c",
    "..%255c",
    "..%c0%af",
}

# File type magic numbers (for validation)
ALLOWED_FILE_SIGNATURES: Set[bytes] = {
    b"",  # Empty file (text)
    b"\x00",  # Null byte
    b"\xff\xfe",  # UTF-16 LE BOM
    b"\xfe\xff",  # UTF-16 BE BOM
    b"\xef\xbb\xbf",  # UTF-8 BOM
}

# =============================================================================
# BOOLEAN VALUE MAPPINGS
# =============================================================================

# True values (case-insensitive)
TRUE_VALUES: Set[str] = {
    "true",
    "yes",
    "1",
    "on",
    "enable",
    "enabled",
    "active",
    "ok",
    "y",
    "t",
}

# False values (case-insensitive)
FALSE_VALUES: Set[str] = {
    "false",
    "no",
    "0",
    "off",
    "disable",
    "disabled",
    "inactive",
    "n",
    "f",
    "null",
    "none",
    "",
}

# =============================================================================
# FILE PATTERNS
# =============================================================================

# Environment file names to search for (in priority order)
ENV_FILE_PATTERNS: List[str] = [
    ".env",
    ".env.local",
    ".env.development",
    ".env.production",
    ".env.staging",
    ".env.test",
    "env",
    "environment",
]

# Directories to exclude from search
EXCLUDED_DIRECTORIES: Set[str] = {
    "__pycache__",
    ".git",
    ".svn",
    ".hg",
    ".bzr",
    "node_modules",
    ".venv",
    "venv",
    "env",
    ".pytest_cache",
    ".mypy_cache",
    ".coverage",
    "build",
    "dist",
    ".tox",
    ".cache",
}

# File extensions to consider
VALID_ENV_EXTENSIONS: Set[str] = {"", ".env", ".txt", ".conf", ".config", ".cfg"}

# =============================================================================
# ENCODING AND CHARSET
# =============================================================================

# Supported encodings (in priority order)
SUPPORTED_ENCODINGS: List[str] = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "ascii"]

# Default encoding
DEFAULT_ENCODING = "utf-8"

# Line ending patterns
LINE_ENDINGS: Set[str] = {"\n", "\r\n", "\r"}

# =============================================================================
# LOGGING AND MONITORING
# =============================================================================

# Security log levels
LOG_LEVELS = {
    "DEBUG": 10,
    "INFO": 20,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50,
    "SECURITY": 60,  # Custom level for security events
}

# Operations to log
LOGGED_OPERATIONS: Set[str] = {
    "load",
    "get",
    "set",
    "delete",
    "clear",
    "scan",
    "validate",
    "parse",
    "access",
    "integrity_check",
}

# Security events to monitor
SECURITY_EVENTS: Set[str] = {
    "path_traversal_attempt",
    "oversized_file",
    "invalid_input",
    "unauthorized_access",
    "integrity_violation",
    "suspicious_pattern",
    "rate_limit_exceeded",
    "session_violation",
}

# =============================================================================
# PERFORMANCE TUNING
# =============================================================================

# Buffer sizes
READ_BUFFER_SIZE = 8192  # 8KB
HASH_BUFFER_SIZE = 4096  # 4KB
WRITE_BUFFER_SIZE = 4096  # 4KB

# Timeout settings (in seconds)
FILE_READ_TIMEOUT = 30
NETWORK_TIMEOUT = 10
LOCK_TIMEOUT = 5

# Cache settings
CACHE_TTL = 300  # 5 minutes
CACHE_MAX_ENTRIES = 1000

# =============================================================================
# ENVIRONMENT SPECIFIC
# =============================================================================

# Development environment settings
DEV_SETTINGS = {
    "strict_validation": False,
    "show_warnings": True,
    "detailed_errors": True,
    "log_level": "DEBUG",
}

# Production environment settings
PROD_SETTINGS = {
    "strict_validation": True,
    "show_warnings": False,
    "detailed_errors": False,
    "log_level": "ERROR",
}

# Testing environment settings
TEST_SETTINGS = {
    "strict_validation": True,
    "show_warnings": True,
    "detailed_errors": True,
    "log_level": "INFO",
    "mock_security": True,
}

# =============================================================================
# REGEX PATTERNS
# =============================================================================

# Key validation pattern (alphanumeric + underscore + hyphen)
KEY_PATTERN = r"^[a-zA-Z][a-zA-Z0-9_-]*$"

# Value patterns
QUOTED_VALUE_PATTERN = r'^(["\'])(.*?)\1$'
VARIABLE_SUBSTITUTION_PATTERN = r"\$\{([^}]+)\}"
COMMENT_PATTERN = r"^\s*#.*$"
EMPTY_LINE_PATTERN = r"^\s*$"

# Path validation patterns
SAFE_PATH_PATTERN = r"^[a-zA-Z0-9._/-]+$"
ABSOLUTE_PATH_PATTERN = r"^[/\\].*"

# =============================================================================
# ERROR CODES
# =============================================================================

# Error code ranges
ERROR_CODE_RANGES = {
    "general": (1, 99),
    "security": (100, 199),
    "parsing": (200, 299),
    "configuration": (300, 399),
    "network": (400, 499),
    "system": (500, 599),
}

# Specific error codes
ERROR_CODES = {
    "SE001": "General SimpleEnvs error",
    "SE100": "Security error",
    "SE101": "Path traversal detected",
    "SE102": "File size limit exceeded",
    "SE103": "Invalid input detected",
    "SE104": "Access denied",
    "SE105": "Integrity check failed",
    "SE106": "Session error",
    "SE107": "Memory security violation",
    "SE200": "File parsing error",
    "SE201": "Environment not loaded",
    "SE202": "Key not found",
    "SE203": "Type conversion error",
    "SE300": "Configuration error",
}

# =============================================================================
# FEATURE FLAGS
# =============================================================================

# Feature toggles
FEATURES = {
    "async_loading": True,
    "file_integrity_check": True,
    "access_logging": True,
    "type_validation": True,
    "path_validation": True,
    "size_validation": True,
    "encoding_detection": True,
    "variable_substitution": False,  # Future feature
    "encryption": False,  # Future feature
    "remote_loading": False,  # Future feature
    "hot_reload": False,  # Future feature
}

# =============================================================================
# VERSION AND METADATA
# =============================================================================

# Version information
VERSION = "2.0.0-beta.1"
API_VERSION = "1.0"
MIN_PYTHON_VERSION = (3, 7)

# Library metadata
LIBRARY_NAME = "SimpleEnvs-Python"
AUTHOR = "vmintf"
DESCRIPTION = "Ultra-secure, high-performance .env file loader"
LICENSE = "MIT"
HOMEPAGE = "https://github.com/vmintf/SimpleEnvs-Python"


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def get_environment_type() -> str:
    """Detect current environment type"""
    env_type = os.getenv("ENVIRONMENT", os.getenv("ENV", "development")).lower()

    if env_type in ("prod", "production"):
        return "production"
    elif env_type in ("test", "testing"):
        return "testing"
    elif env_type in ("stage", "staging"):
        return "staging"
    else:
        return "development"


def get_settings_for_environment() -> dict:
    """Get settings based on current environment"""
    env_type = get_environment_type()

    if env_type == "production":
        return PROD_SETTINGS.copy()
    elif env_type == "testing":
        return TEST_SETTINGS.copy()
    else:
        return DEV_SETTINGS.copy()


def is_feature_enabled(feature_name: str) -> bool:
    """Check if a feature is enabled"""
    return FEATURES.get(feature_name, False)


def get_max_value_for_environment(setting_name: str) -> int:
    """Get environment-specific maximum values"""
    env_type = get_environment_type()

    # Stricter limits in production
    if env_type == "production":
        multiplier = 0.8
    elif env_type == "testing":
        multiplier = 0.5
    else:
        multiplier = 1.0

    base_values = {
        "max_file_size": MAX_FILE_SIZE,
        "max_entries": MAX_ENTRIES_PER_DIRECTORY,
        "max_variables": MAX_VARIABLE_COUNT,
    }

    base_value = base_values.get(setting_name, 1000)
    return int(base_value * multiplier)


if __name__ == "__main__":
    # Test and display current configuration
    print(f"SimpleEnvs v{VERSION}")
    print(f"Environment: {get_environment_type()}")
    print(f"Settings: {get_settings_for_environment()}")
    print(f"Max file size: {get_max_value_for_environment('max_file_size'):,} bytes")
    print(f"Features enabled: {[k for k, v in FEATURES.items() if v]}")
    print(f"Security patterns: {len(DANGEROUS_PATTERNS)} patterns monitored")
    print(f"Supported encodings: {', '.join(SUPPORTED_ENCODINGS)}")
