#!/usr/bin/env python3
"""
SimpleEnvs: Exception classes for error handling
"""

from typing import Any, Optional


class SimpleEnvsError(Exception):
    """Base exception for all SimpleEnvs errors"""

    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.details = details

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} (Details: {self.details})"
        return self.message


class EnvSecurityError(SimpleEnvsError):
    """Base security exception for SecureEnvLoader"""

    pass


class PathTraversalError(EnvSecurityError):
    """Path traversal attack detected"""

    def __init__(self, path: str):
        super().__init__(f"Path traversal detected: {path}", {"attempted_path": path})
        self.attempted_path = path


class FileSizeError(EnvSecurityError):
    """File size exceeds security limits"""

    def __init__(self, file_path: str, size: int, max_size: int):
        super().__init__(
            f"File too large: {size} bytes (max: {max_size})",
            {"file_path": file_path, "size": size, "max_size": max_size},
        )
        self.file_path = file_path
        self.size = size
        self.max_size = max_size


class InvalidInputError(EnvSecurityError):
    """Input validation failed"""

    def __init__(self, message: str, input_value: Optional[str] = None):
        details = {"input_value": input_value} if input_value else None
        super().__init__(message, details)
        self.input_value = input_value


class AccessDeniedError(EnvSecurityError):
    """Access to internal methods denied"""

    def __init__(self, operation: str, caller: Optional[str] = None):
        message = f"Access denied for operation: {operation}"
        if caller:
            message += f" (caller: {caller})"
        super().__init__(message, {"operation": operation, "caller": caller})
        self.operation = operation
        self.caller = caller


class FileParsingError(SimpleEnvsError):
    """Error occurred during file parsing"""

    def __init__(
        self,
        file_path: str,
        line_number: Optional[int] = None,
        original_error: Optional[Exception] = None,
    ):
        message = f"Failed to parse file: {file_path}"
        if line_number:
            message += f" at line {line_number}"

        details = {
            "file_path": file_path,
            "line_number": line_number,
            "original_error": str(original_error) if original_error else None,
        }

        super().__init__(message, details)
        self.file_path = file_path
        self.line_number = line_number
        self.original_error = original_error


class EnvNotLoadedError(SimpleEnvsError):
    """Environment variables not loaded yet"""

    def __init__(self, operation: str):
        super().__init__(
            f"Environment not loaded. Call load() or load_secure() before {operation}",
            {"operation": operation},
        )
        self.operation = operation


class KeyNotFoundError(SimpleEnvsError):
    """Environment variable key not found"""

    def __init__(self, key: str, available_keys: Optional[list] = None):
        message = f"Environment variable '{key}' not found"
        if available_keys:
            message += f". Available keys: {', '.join(available_keys)}"

        super().__init__(message, {"key": key, "available_keys": available_keys})
        self.key = key
        self.available_keys = available_keys


class TypeConversionError(SimpleEnvsError):
    """Type conversion failed"""

    def __init__(self, key: str, value: Any, target_type: str):
        super().__init__(
            f"Cannot convert '{key}' value '{value}' to {target_type}",
            {"key": key, "value": value, "target_type": target_type},
        )
        self.key = key
        self.value = value
        self.target_type = target_type


class ConfigurationError(SimpleEnvsError):
    """Configuration or setup error"""

    def __init__(self, component: str, issue: str):
        super().__init__(f"Configuration error in {component}: {issue}")
        self.component = component
        self.issue = issue


class IntegrityError(EnvSecurityError):
    """File integrity check failed"""

    def __init__(self, file_path: str, expected_hash: str, actual_hash: str):
        super().__init__(
            f"File integrity check failed for {file_path}",
            {
                "file_path": file_path,
                "expected_hash": expected_hash,
                "actual_hash": actual_hash,
            },
        )
        self.file_path = file_path
        self.expected_hash = expected_hash
        self.actual_hash = actual_hash


class SessionError(EnvSecurityError):
    """Session-related security error"""

    def __init__(self, session_id: str, issue: str):
        super().__init__(f"Session error ({session_id}): {issue}")
        self.session_id = session_id
        self.issue = issue


class MemorySecurityError(EnvSecurityError):
    """Memory security violation"""

    def __init__(self, operation: str, reason: str):
        super().__init__(f"Memory security violation in {operation}: {reason}")
        self.operation = operation
        self.reason = reason


# Utility functions for exception handling
def format_security_error(error: EnvSecurityError) -> str:
    """Format security error for logging"""
    return f"[SECURITY] {error.__class__.__name__}: {error.message}"


def is_security_critical(error: Exception) -> bool:
    """Check if error is security-critical"""
    critical_errors = (
        PathTraversalError,
        AccessDeniedError,
        IntegrityError,
        MemorySecurityError,
    )
    return isinstance(error, critical_errors)


def get_error_code(error: SimpleEnvsError) -> str:
    """Get error code for programmatic handling"""
    error_codes = {
        SimpleEnvsError: "SE001",
        EnvSecurityError: "SE100",
        PathTraversalError: "SE101",
        FileSizeError: "SE102",
        InvalidInputError: "SE103",
        AccessDeniedError: "SE104",
        IntegrityError: "SE105",
        SessionError: "SE106",
        MemorySecurityError: "SE107",
        FileParsingError: "SE200",
        EnvNotLoadedError: "SE201",
        KeyNotFoundError: "SE202",
        TypeConversionError: "SE203",
        ConfigurationError: "SE300",
    }
    return error_codes.get(type(error), "SE000")


# Exception context manager for secure error handling
class SecureErrorHandler:
    """Context manager for secure error handling"""

    def __init__(self, operation: str, suppress_details: bool = False):
        self.operation = operation
        self.suppress_details = suppress_details

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type and issubclass(exc_type, EnvSecurityError):
            # Log security error without exposing sensitive details
            if self.suppress_details:
                error_msg = f"Security error in {self.operation}"
                print(f"[SECURITY] {error_msg}")
            else:
                print(f"[SECURITY] {format_security_error(exc_value)}")

            # Don't suppress the exception, let it propagate
            return False

        return False


# Custom exception handler for different environments
def handle_simpleenvs_error(error: Exception, environment: str = "production") -> str:
    """Handle SimpleEnvs errors based on environment"""

    if environment == "development":
        # Show full details in development
        if isinstance(error, SimpleEnvsError):
            return f"{error.__class__.__name__}: {error.message} | Details: {error.details}"
        return str(error)

    elif environment == "production":
        # Hide sensitive details in production
        if isinstance(error, EnvSecurityError):
            return f"Security error occurred. Error code: {get_error_code(error)}"
        elif isinstance(error, SimpleEnvsError):
            return f"Configuration error. Error code: {get_error_code(error)}"
        return "An unexpected error occurred."

    else:
        # Default handling
        return str(error)


if __name__ == "__main__":
    # Example usage and testing
    try:
        raise PathTraversalError("../../../etc/passwd")
    except PathTraversalError as e:
        print(f"Caught: {e}")
        print(f"Error code: {get_error_code(e)}")
        print(f"Is critical: {is_security_critical(e)}")
        print(f"Formatted: {format_security_error(e)}")
        print(f"Production message: {handle_simpleenvs_error(e, 'production')}")
        print(f"Development message: {handle_simpleenvs_error(e, 'development')}")

    # Test context manager
    with SecureErrorHandler("test_operation", suppress_details=True):
        try:
            raise InvalidInputError("Test validation error", "bad_input")
        except InvalidInputError:
            print("Security error handled by context manager")
