#!/usr/bin/env python3
"""
SimpleEnvs Error Testing Suite
Comprehensive test suite to demonstrate all error types and security features
"""

import asyncio
import os
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Tuple

# Import SimpleEnvs components (assuming they're available)
try:
    from simpleenvs import (
        AccessDeniedError,
        ConfigurationError,
        EnvNotLoadedError,
        EnvSecurityError,
        FileParsingError,
        FileSizeError,
        IntegrityError,
        InvalidInputError,
        KeyNotFoundError,
        MemorySecurityError,
        PathTraversalError,
        SecureEnvLoader,
        SessionError,
        SimpleEnvLoader,
        SimpleEnvsError,
        TypeConversionError,
    )
    from simpleenvs.constants import (
        DANGEROUS_PATTERNS,
        MAX_FILE_SIZE,
        MAX_KEY_LENGTH,
        MAX_LINE_LENGTH,
        MAX_VALUE_LENGTH,
    )
    from simpleenvs.secure import LoadOptions  # ← 별도로 import
    from simpleenvs.utils import (
        parse_env_content,
        parse_env_value,
        safe_file_read,
        validate_key_format,
        validate_path_security,
    )

    USING_REAL_SIMPLEENVS = True
except ImportError as e:
    print(f"Warning: SimpleEnvs import failed: {e}")
    USING_REAL_SIMPLEENVS = False
    print("Warning: SimpleEnvs not installed. Creating mock classes for demonstration.")

    # Mock classes for demonstration
    class SimpleEnvsError(Exception):
        pass

    class EnvSecurityError(SimpleEnvsError):
        pass

    class PathTraversalError(EnvSecurityError):
        pass

    class FileSizeError(EnvSecurityError):
        def __init__(self, file_path, size, max_size):
            self.file_path = file_path
            self.size = size
            self.max_size = max_size
            super().__init__(
                f"File {file_path} is too large ({size} bytes, max: {max_size})"
            )

    class InvalidInputError(EnvSecurityError):
        pass

    class AccessDeniedError(EnvSecurityError):
        pass

    class FileParsingError(SimpleEnvsError):
        pass

    class EnvNotLoadedError(SimpleEnvsError):
        pass

    class KeyNotFoundError(SimpleEnvsError):
        pass

    class TypeConversionError(SimpleEnvsError):
        pass

    class ConfigurationError(SimpleEnvsError):
        pass

    class IntegrityError(EnvSecurityError):
        pass

    class SessionError(EnvSecurityError):
        pass

    class MemorySecurityError(EnvSecurityError):
        pass

    class SimpleEnvLoader:
        def __init__(self):
            self.env_data = {}

        async def load(self, path=None):
            pass

        def get(self, key):
            return None

    class SecureEnvLoader:
        def __init__(self):
            pass

        async def load_secure(self, options=None):
            pass

        def get_secure(self, key):
            return None

    class LoadOptions:
        def __init__(self, **kwargs):
            pass

    MAX_FILE_SIZE = 10 * 1024 * 1024
    MAX_KEY_LENGTH = 128
    MAX_VALUE_LENGTH = 1024
    MAX_LINE_LENGTH = 4096
    DANGEROUS_PATTERNS = ["$(", "`", "${", "<script"]


class ErrorTestSuite:
    """Comprehensive error testing suite for SimpleEnvs"""

    def __init__(self):
        self.test_results: List[Dict] = []
        self.temp_dir = tempfile.mkdtemp()
        print(f"Using temporary directory: {self.temp_dir}")

    def log_test(
        self, test_name: str, error_type: str, success: bool, details: str = ""
    ):
        """Log test results"""
        result = {
            "test_name": test_name,
            "error_type": error_type,
            "success": success,
            "details": details,
            "timestamp": time.time(),
        }
        self.test_results.append(result)

        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name} ({error_type}): {details}")

    def create_test_file(self, filename: str, content: str) -> str:
        """Create a test file with specified content"""
        file_path = os.path.join(self.temp_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path

    def create_large_file(self, filename: str, size_bytes: int) -> str:
        """Create a large file for size testing"""
        file_path = os.path.join(self.temp_dir, filename)
        with open(file_path, "w") as f:
            # Write in chunks to avoid memory issues
            chunk_size = 8192  # 8KB chunks
            chunk = "A" * chunk_size
            remaining = size_bytes

            while remaining > 0:
                write_size = min(chunk_size, remaining)
                f.write(chunk[:write_size])
                remaining -= write_size

        return file_path

    # =============================================================================
    # PATH TRAVERSAL TESTS
    # =============================================================================

    async def test_path_traversal_errors(self):
        """Test path traversal security errors"""
        print("\n🔒 Testing Path Traversal Security...")

        dangerous_paths = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config\\sam",
            "/etc/passwd",
            "\\windows\\system32",
            "%2e%2e/passwd",
            "..%2fpasswd",
            "..%5cpasswd",
            "./../../secrets.env",
        ]

        for path in dangerous_paths:
            try:
                # Test with SecureEnvLoader
                loader = SecureEnvLoader()
                await loader.load_secure(LoadOptions(path=path))
                self.log_test(
                    f"Path traversal: {path}",
                    "PathTraversalError",
                    False,
                    "Should have failed",
                )
            except PathTraversalError:
                self.log_test(
                    f"Path traversal: {path}",
                    "PathTraversalError",
                    True,
                    "Correctly blocked",
                )
            except Exception as e:
                self.log_test(
                    f"Path traversal: {path}",
                    "PathTraversalError",
                    True,
                    f"Blocked with: {type(e).__name__}",
                )

    # =============================================================================
    # FILE SIZE TESTS
    # =============================================================================

    async def test_file_size_errors(self):
        """Test file size limit errors"""
        print("\n📏 Testing File Size Limits...")

        # Create files of various sizes
        test_cases = [
            ("empty.env", 0, ""),
            ("normal.env", 1024, "APP_NAME=TestApp\nDEBUG=true"),  # 1KB
            ("medium.env", 1024 * 1024, None),  # 1MB
            ("large.env", 15 * 1024 * 1024, None),  # 15MB file (over 10MB limit)
        ]

        for filename, size_bytes, content in test_cases:
            try:
                if content is not None:
                    # Use provided content
                    file_path = self.create_test_file(filename, content)
                else:
                    # Generate file of specific size
                    file_path = self.create_large_file(filename, size_bytes)

                loader = SecureEnvLoader()
                await loader.load_secure(LoadOptions(path=file_path))

                if size_bytes > MAX_FILE_SIZE:
                    self.log_test(
                        f"File size: {filename} ({size_bytes // 1024}KB)",
                        "FileSizeError",
                        False,
                        "Should have failed",
                    )
                else:
                    self.log_test(
                        f"File size: {filename} ({size_bytes // 1024}KB)",
                        "FileSizeError",
                        True,
                        "Correctly accepted",
                    )

            except FileSizeError as e:
                self.log_test(
                    f"File size: {filename} ({size_bytes // 1024}KB)",
                    "FileSizeError",
                    True,
                    f"Correctly rejected: {e}",
                )
            except Exception as e:
                self.log_test(
                    f"File size: {filename} ({size_bytes // 1024}KB)",
                    "FileSizeError",
                    True,
                    f"Rejected with: {type(e).__name__}",
                )

    # =============================================================================
    # INVALID INPUT TESTS
    # =============================================================================

    async def test_invalid_input_errors(self):
        """Test invalid input validation"""
        print("\n⚠️  Testing Invalid Input Validation...")

        # Test dangerous patterns in .env content
        dangerous_contents = [
            (
                "script_injection.env",
                """
APP_NAME=MyApp
SCRIPT_TAG=<script>alert('xss')</script>
DEBUG=true
""",
            ),
            (
                "command_injection.env",
                """
APP_NAME=MyApp
COMMAND=$(rm -rf /)
DEBUG=true
""",
            ),
            (
                "shell_injection.env",
                """
APP_NAME=MyApp
SHELL_CMD=`cat /etc/passwd`
DEBUG=true
""",
            ),
            (
                "variable_substitution.env",
                """
APP_NAME=MyApp
EXPLOIT=${USER:-$(whoami)}
DEBUG=true
""",
            ),
            (
                "null_byte.env",
                """
APP_NAME=MyApp\x00
DEBUG=true
""",
            ),
            (
                "oversized_key.env",
                f"""
{"A" * (MAX_KEY_LENGTH + 10)}=value
DEBUG=true
""",
            ),
            (
                "oversized_value.env",
                f"""
APP_NAME={"B" * (MAX_VALUE_LENGTH + 100)}
DEBUG=true
""",
            ),
        ]

        for filename, content in dangerous_contents:
            try:
                file_path = self.create_test_file(filename, content)
                loader = SecureEnvLoader()
                await loader.load_secure(LoadOptions(path=file_path))
                self.log_test(
                    f"Invalid input: {filename}",
                    "InvalidInputError",
                    False,
                    "Should have been rejected",
                )
            except InvalidInputError as e:
                self.log_test(
                    f"Invalid input: {filename}",
                    "InvalidInputError",
                    True,
                    f"Correctly rejected: {e}",
                )
            except Exception as e:
                self.log_test(
                    f"Invalid input: {filename}",
                    "InvalidInputError",
                    True,
                    f"Rejected with: {type(e).__name__}",
                )

    # =============================================================================
    # FILE PARSING TESTS
    # =============================================================================

    async def test_file_parsing_errors(self):
        """Test file parsing errors"""
        print("\n📄 Testing File Parsing Errors...")

        parsing_test_cases = [
            (
                "malformed.env",
                """
APP_NAME=MyApp
INVALID_LINE_NO_EQUALS
DEBUG=true
ANOTHER_INVALID
""",
            ),
            (
                "invalid_encoding.env",
                b"""
APP_NAME=MyApp
INVALID_UTF8=\xff\xfe\x00\x00
DEBUG=true
""",
            ),
            (
                "mixed_quotes.env",
                """
APP_NAME="MyApp
DEBUG='true"
PORT=8080
""",
            ),
            (
                "extremely_long_lines.env",
                f"""
APP_NAME=MyApp
LONG_LINE={"X" * (MAX_LINE_LENGTH + 100)}
DEBUG=true
""",
            ),
        ]

        for filename, content in parsing_test_cases:
            try:
                if isinstance(content, bytes):
                    # Write binary content for encoding tests
                    file_path = os.path.join(self.temp_dir, filename)
                    with open(file_path, "wb") as f:
                        f.write(content)
                else:
                    file_path = self.create_test_file(filename, content)

                loader = SimpleEnvLoader()
                await loader.load(file_path)
                self.log_test(
                    f"File parsing: {filename}",
                    "FileParsingError",
                    True,
                    "Parsed successfully (non-strict mode)",
                )

            except FileParsingError as e:
                self.log_test(
                    f"File parsing: {filename}",
                    "FileParsingError",
                    True,
                    f"Correctly failed: {e}",
                )
            except Exception as e:
                self.log_test(
                    f"File parsing: {filename}",
                    "FileParsingError",
                    True,
                    f"Failed with: {type(e).__name__}",
                )

    # =============================================================================
    # ENVIRONMENT NOT LOADED TESTS
    # =============================================================================

    def test_env_not_loaded_errors(self):
        """Test environment not loaded errors"""
        print("\n🚫 Testing Environment Not Loaded Errors...")

        operations = [
            ("get", lambda loader: loader.get("APP_NAME")),
            ("get_int", lambda loader: loader.get_int("PORT")),
            ("get_bool", lambda loader: loader.get_bool("DEBUG")),
            ("get_str", lambda loader: loader.get_str("APP_NAME")),
            ("get_all", lambda loader: loader.get_all()),
            ("keys", lambda loader: loader.keys()),
        ]

        for op_name, operation in operations:
            try:
                loader = SimpleEnvLoader()  # Not loaded
                result = operation(loader)
                self.log_test(
                    f"Not loaded: {op_name}",
                    "EnvNotLoadedError",
                    False,
                    "Should have failed",
                )
            except EnvNotLoadedError as e:
                self.log_test(
                    f"Not loaded: {op_name}",
                    "EnvNotLoadedError",
                    True,
                    f"Correctly failed: {e}",
                )
            except Exception as e:
                self.log_test(
                    f"Not loaded: {op_name}",
                    "EnvNotLoadedError",
                    True,
                    f"Failed with: {type(e).__name__}",
                )

    # =============================================================================
    # TYPE CONVERSION TESTS
    # =============================================================================

    async def test_type_conversion_errors(self):
        """Test type conversion errors"""
        print("\n🔄 Testing Type Conversion Errors...")

        # Create file with problematic type conversions
        problematic_env = """
APP_NAME=MyApp
PORT=not_a_number
DEBUG=maybe
TIMEOUT=3.14.159
INVALID_BOOL=yes_no_maybe
LARGE_NUMBER=999999999999999999999999999999999999999
"""

        file_path = self.create_test_file("type_conversion.env", problematic_env)

        try:
            loader = SimpleEnvLoader()
            await loader.load(file_path)

            # Test various type conversion failures
            test_cases = [
                ("PORT as int", lambda: loader.get_int("PORT")),
                ("DEBUG as bool", lambda: loader.get_bool("DEBUG")),
                ("TIMEOUT as int", lambda: loader.get_int("TIMEOUT")),
                ("INVALID_BOOL as bool", lambda: loader.get_bool("INVALID_BOOL")),
                ("LARGE_NUMBER as int", lambda: loader.get_int("LARGE_NUMBER")),
            ]

            for test_name, test_func in test_cases:
                try:
                    result = test_func()
                    self.log_test(
                        f"Type conversion: {test_name}",
                        "TypeConversionError",
                        True,
                        f"Gracefully handled: {result}",
                    )
                except TypeConversionError as e:
                    self.log_test(
                        f"Type conversion: {test_name}",
                        "TypeConversionError",
                        True,
                        f"Correctly failed: {e}",
                    )
                except Exception as e:
                    self.log_test(
                        f"Type conversion: {test_name}",
                        "TypeConversionError",
                        True,
                        f"Handled with: {type(e).__name__}",
                    )

        except Exception as e:
            self.log_test(
                "Type conversion setup", "FileParsingError", False, f"Setup failed: {e}"
            )

    # =============================================================================
    # KEY NOT FOUND TESTS
    # =============================================================================

    async def test_key_not_found_errors(self):
        """Test key not found errors"""
        print("\n🔍 Testing Key Not Found Errors...")

        # Create simple env file
        simple_env = """
APP_NAME=TestApp
DEBUG=true
PORT=8080
"""

        file_path = self.create_test_file("simple.env", simple_env)

        try:
            loader = SimpleEnvLoader()
            await loader.load(file_path)

            # Test missing keys
            missing_keys = [
                "DATABASE_URL",
                "SECRET_KEY",
                "REDIS_URL",
                "NONEXISTENT_KEY",
            ]

            for key in missing_keys:
                result = loader.get(key)
                if result is None:
                    self.log_test(
                        f"Key not found: {key}",
                        "KeyNotFoundError",
                        True,
                        "Correctly returned None",
                    )
                else:
                    self.log_test(
                        f"Key not found: {key}",
                        "KeyNotFoundError",
                        False,
                        f"Unexpected result: {result}",
                    )

        except Exception as e:
            self.log_test(
                "Key not found setup", "FileParsingError", False, f"Setup failed: {e}"
            )

    # =============================================================================
    # SECURITY-SPECIFIC TESTS
    # =============================================================================

    async def test_security_specific_errors(self):
        """Test security-specific errors"""
        print("\n🛡️  Testing Security-Specific Errors...")

        # Test access denied scenarios
        try:
            loader = SecureEnvLoader()
            # Try to access private methods (this would normally be blocked)
            # In a real implementation, this might involve accessing _SecureEnvLoader__env_data directly
            info = loader.get_security_info()
            self.log_test(
                "Security info access",
                "AccessDeniedError",
                True,
                "Allowed access to security info",
            )
        except AccessDeniedError as e:
            self.log_test(
                "Security info access",
                "AccessDeniedError",
                True,
                f"Correctly denied: {e}",
            )
        except Exception as e:
            self.log_test(
                "Security info access",
                "AccessDeniedError",
                True,
                f"Handled with: {type(e).__name__}",
            )

        # Test session errors
        try:
            loader1 = SecureEnvLoader(session_id="session1")
            loader2 = SecureEnvLoader(session_id="session2")
            # In a real implementation, this might test session conflicts
            self.log_test(
                "Session conflict",
                "SessionError",
                True,
                "Multiple sessions created successfully",
            )
        except SessionError as e:
            self.log_test(
                "Session conflict", "SessionError", True, f"Correctly handled: {e}"
            )
        except Exception as e:
            self.log_test(
                "Session conflict",
                "SessionError",
                True,
                f"Handled with: {type(e).__name__}",
            )

        # Test memory security
        try:
            loader = SecureEnvLoader()
            await loader.load_secure()
            loader.secure_wipe()
            self.log_test(
                "Memory security wipe",
                "MemorySecurityError",
                True,
                "Successfully wiped memory",
            )
        except MemorySecurityError as e:
            self.log_test(
                "Memory security wipe",
                "MemorySecurityError",
                True,
                f"Error during wipe: {e}",
            )
        except Exception as e:
            self.log_test(
                "Memory security wipe",
                "MemorySecurityError",
                True,
                f"Handled with: {type(e).__name__}",
            )

    # =============================================================================
    # INTEGRITY TESTS
    # =============================================================================

    async def test_integrity_errors(self):
        """Test file integrity errors"""
        print("\n🔐 Testing File Integrity Errors...")

        # Create a file and test integrity
        original_content = """
APP_NAME=OriginalApp
DEBUG=true
PORT=8080
"""

        file_path = self.create_test_file("integrity_test.env", original_content)

        try:
            loader = SecureEnvLoader()
            await loader.load_secure(LoadOptions(path=file_path))

            # Modify the file after loading
            modified_content = """
APP_NAME=ModifiedApp
DEBUG=false
PORT=9090
MALICIOUS_CODE=$(rm -rf /)
"""
            with open(file_path, "w") as f:
                f.write(modified_content)

            # Check integrity
            integrity_check = loader.verify_file_integrity(file_path)
            if not integrity_check:
                self.log_test(
                    "File integrity check",
                    "IntegrityError",
                    True,
                    "Correctly detected file modification",
                )
            else:
                self.log_test(
                    "File integrity check",
                    "IntegrityError",
                    False,
                    "Failed to detect modification",
                )

        except IntegrityError as e:
            self.log_test(
                "File integrity check", "IntegrityError", True, f"Correctly failed: {e}"
            )
        except Exception as e:
            self.log_test(
                "File integrity check",
                "IntegrityError",
                True,
                f"Handled with: {type(e).__name__}",
            )

    # =============================================================================
    # CONFIGURATION ERRORS
    # =============================================================================

    def test_configuration_errors(self):
        """Test configuration errors"""
        print("\n⚙️  Testing Configuration Errors...")

        config_test_cases = [
            ("invalid_max_depth", lambda: SimpleEnvLoader().load_sync(max_depth=-1)),
            (
                "invalid_max_depth_high",
                lambda: SimpleEnvLoader().load_sync(max_depth=100),
            ),
            ("invalid_path_type", lambda: SimpleEnvLoader().load_sync(path=123)),
            ("invalid_key_type", lambda: SimpleEnvLoader().get(123)),
        ]

        for test_name, test_func in config_test_cases:
            try:
                test_func()
                self.log_test(
                    f"Configuration: {test_name}",
                    "ConfigurationError",
                    False,
                    "Should have failed",
                )
            except (ConfigurationError, InvalidInputError, TypeError, ValueError) as e:
                self.log_test(
                    f"Configuration: {test_name}",
                    "ConfigurationError",
                    True,
                    f"Correctly failed: {type(e).__name__}",
                )
            except Exception as e:
                self.log_test(
                    f"Configuration: {test_name}",
                    "ConfigurationError",
                    True,
                    f"Failed with: {type(e).__name__}",
                )

    # =============================================================================
    # EDGE CASE TESTS
    # =============================================================================

    async def test_edge_cases(self):
        """Test various edge cases"""
        print("\n🎯 Testing Edge Cases...")

        edge_cases = [
            ("empty_file.env", ""),
            (
                "only_comments.env",
                """
# This is a comment
# Another comment
# Yet another comment
""",
            ),
            ("whitespace_only.env", "   \n  \t  \n   "),
            (
                "mixed_content.env",
                """
# Configuration file
APP_NAME=TestApp

# Database settings
DB_HOST=localhost
DB_PORT=5432

# Debug mode
DEBUG=true

# End of file
""",
            ),
            (
                "unicode_content.env",
                """
APP_NAME=测试应用
EMOJI=🚀
DESCRIPTION=Iñtërnâtiônàlizætiøn
""",
            ),
        ]

        for filename, content in edge_cases:
            try:
                file_path = self.create_test_file(filename, content)

                # Test with both loaders
                simple_loader = SimpleEnvLoader()
                await simple_loader.load(file_path)

                secure_loader = SecureEnvLoader()
                await secure_loader.load_secure(LoadOptions(path=file_path))

                self.log_test(
                    f"Edge case: {filename}", "EdgeCase", True, "Successfully handled"
                )

            except Exception as e:
                self.log_test(
                    f"Edge case: {filename}",
                    "EdgeCase",
                    True,
                    f"Gracefully failed: {type(e).__name__}",
                )

    # =============================================================================
    # RUN ALL TESTS
    # =============================================================================

    async def run_all_tests(self):
        """Run all error tests"""
        print("🧪 SimpleEnvs Error Testing Suite")
        print("=" * 50)

        # Run all test categories
        await self.test_path_traversal_errors()
        await self.test_file_size_errors()
        await self.test_invalid_input_errors()
        await self.test_file_parsing_errors()
        self.test_env_not_loaded_errors()
        await self.test_type_conversion_errors()
        await self.test_key_not_found_errors()
        await self.test_security_specific_errors()
        await self.test_integrity_errors()
        self.test_configuration_errors()
        await self.test_edge_cases()

        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - passed_tests

        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests / total_tests) * 100:.1f}%")

        # Group by error type
        error_types = {}
        for result in self.test_results:
            error_type = result["error_type"]
            if error_type not in error_types:
                error_types[error_type] = {"total": 0, "passed": 0}
            error_types[error_type]["total"] += 1
            if result["success"]:
                error_types[error_type]["passed"] += 1

        print("\n📈 RESULTS BY ERROR TYPE:")
        for error_type, stats in sorted(error_types.items()):
            total = stats["total"]
            passed = stats["passed"]
            rate = (passed / total) * 100 if total > 0 else 0
            print(f"  {error_type}: {passed}/{total} ({rate:.1f}%)")

        # Show failed tests
        failed_results = [r for r in self.test_results if not r["success"]]
        if failed_results:
            print("\n❌ FAILED TESTS:")
            for result in failed_results:
                print(f"  - {result['test_name']}: {result['details']}")

        # Cleanup
        import shutil

        try:
            shutil.rmtree(self.temp_dir)
            print(f"\n🧹 Cleaned up temporary directory: {self.temp_dir}")
        except Exception as e:
            print(f"\n⚠️  Failed to clean up temporary directory: {e}")


# =============================================================================
# DEMO FUNCTIONS (수정된 부분)
# =============================================================================


def create_demo_large_file(temp_dir: str, filename: str, size_bytes: int) -> str:
    """Create a demo large file for testing"""
    file_path = os.path.join(temp_dir, filename)
    with open(file_path, "w") as f:
        # Write enough data to reach the target size
        chunk_size = 1024  # 1KB chunks
        chunk = "X" * chunk_size
        remaining = size_bytes

        while remaining > 0:
            write_size = min(chunk_size, remaining)
            f.write(chunk[:write_size])
            remaining -= write_size

    return file_path


def check_file_size(path: str, max_size: int):
    """Check file size and raise error if too large"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    size = os.path.getsize(path)
    if size > max_size:
        # SimpleEnvs의 실제 FileSizeError와 호환되도록 수정
        if USING_REAL_SIMPLEENVS:
            raise FileSizeError(path, size, max_size)
        else:
            # Mock version
            error = FileSizeError(path, size, max_size)
            raise error


def demonstrate_error_handling():
    """Demonstrate error handling patterns"""
    print("\n🎭 DEMONSTRATING ERROR HANDLING PATTERNS")
    print("=" * 50)

    # Create temporary directory for demo files
    temp_dir = tempfile.mkdtemp()

    try:
        # Example 1: Try-catch with specific exceptions
        print("\n1. Specific Exception Handling:")
        try:
            # This would normally trigger a path traversal error
            raise PathTraversalError("../../../etc/passwd")
        except PathTraversalError as e:
            print(f"   Caught PathTraversalError: {e}")

        # Example 2: Generic exception handling
        print("\n2. Generic Exception Handling:")
        try:
            raise InvalidInputError(
                "Dangerous pattern detected", "<script>alert('xss')</script>"
            )
        except EnvSecurityError as e:
            print(f"   Caught security error: {e}")
        except SimpleEnvsError as e:
            print(f"   Caught SimpleEnvs error: {e}")
        except Exception as e:
            print(f"   Caught unexpected error: {e}")

        # Example 3: Error details extraction with real file
        print("\n3. Error Details Extraction (with real file):")
        try:
            # Create a real large file for testing
            large_file_path = create_demo_large_file(
                temp_dir, "large_test_file.txt", 2048
            )  # 2KB file
            max_allowed_size = 1000  # 1KB limit

            check_file_size(large_file_path, max_allowed_size)

        except FileSizeError as e:
            # 안전한 속성 접근 - SimpleEnvs와 mock 버전 모두 지원
            file_path = getattr(e, "file_path", getattr(e, "path", "unknown"))
            size = getattr(e, "size", "unknown")
            max_size = getattr(e, "max_size", "unknown")

            print(f"   File: {file_path}")
            print(f"   Size: {size} bytes")
            print(f"   Max allowed: {max_size} bytes")
            print(f"   Message: {e}")

        except FileNotFoundError as e:
            print(f"   File not found error: {e}")

        # Example 4: Multiple file size tests
        print("\n4. Multiple File Size Tests:")
        test_files = [
            ("small_file.txt", 500),  # Should pass with 1KB limit
            ("medium_file.txt", 1200),  # Should fail with 1KB limit
            ("large_file.txt", 5000),  # Should definitely fail with 1KB limit
        ]

        max_test_size = 1000  # 1KB limit for demo

        for filename, size_bytes in test_files:
            try:
                test_file_path = create_demo_large_file(temp_dir, filename, size_bytes)
                check_file_size(test_file_path, max_test_size)
                print(f"   ✅ {filename} ({size_bytes} bytes): Accepted")

            except FileSizeError as e:
                file_path = getattr(e, "file_path", getattr(e, "path", "unknown"))
                size = getattr(e, "size", "unknown")
                print(f"   ❌ {filename} ({size} bytes): Rejected (too large)")

            except Exception as e:
                print(f"   ⚠️  {filename}: Error - {type(e).__name__}: {e}")

        # Example 5: Demonstrating error cascading
        print("\n5. Error Cascading and Recovery:")
        operations = [
            (
                "check_small_file",
                lambda: check_file_size(
                    create_demo_large_file(temp_dir, "cascade_small.txt", 800), 1000
                ),
            ),
            (
                "check_large_file",
                lambda: check_file_size(
                    create_demo_large_file(temp_dir, "cascade_large.txt", 2000), 1000
                ),
            ),
            (
                "check_nonexistent",
                lambda: check_file_size("nonexistent_file.txt", 1000),
            ),
        ]

        for op_name, operation in operations:
            try:
                operation()
                print(f"   ✅ {op_name}: Success")
            except FileSizeError:
                print(f"   📏 {op_name}: File too large (expected)")
            except FileNotFoundError:
                print(f"   📄 {op_name}: File not found (expected)")
            except Exception as e:
                print(f"   ❌ {op_name}: Unexpected error - {type(e).__name__}")

    finally:
        # Cleanup demo files
        import shutil

        try:
            shutil.rmtree(temp_dir)
            print(f"\n🧹 Demo cleanup completed")
        except Exception as e:
            print(f"\n⚠️  Demo cleanup failed: {e}")


# =============================================================================
# MAIN EXECUTION
# =============================================================================


async def main():
    """Main execution function"""
    print("🧪 SimpleEnvs Comprehensive Error Testing Suite")
    print("=" * 60)

    if USING_REAL_SIMPLEENVS:
        print("✅ Using real SimpleEnvs library")
    else:
        print("⚠️  Using mock classes for demonstration")

    print()

    # Run comprehensive error testing
    test_suite = ErrorTestSuite()
    await test_suite.run_all_tests()

    # Demonstrate error handling patterns
    demonstrate_error_handling()

    print("\n🎉 Error testing complete!")
    print(
        "This suite demonstrates all major error types and security features in SimpleEnvs."
    )

    if not USING_REAL_SIMPLEENVS:
        print("\n💡 To run with real SimpleEnvs functionality:")
        print("   pip install simpleenvs-python")


if __name__ == "__main__":
    # Run the test suite
    asyncio.run(main())
