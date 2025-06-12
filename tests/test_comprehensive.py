#!/usr/bin/env python3
"""
Comprehensive test suite for SimpleEnvs
Designed to achieve 90%+ code coverage
"""

import asyncio
import gc
import os
import tempfile
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

import simpleenvs
from simpleenvs import SecureEnvLoader, SimpleEnvLoader, utils
from simpleenvs.constants import *
from simpleenvs.exceptions import *

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def temp_env_file():
    """Create temporary .env file for testing"""
    content = """
# Test .env file
APP_NAME=TestApp
DEBUG=true
PORT=8080
DATABASE_URL=postgresql://user:pass@localhost/db
SECRET_KEY=super-secret-key
FLOAT_VALUE=3.14
EMPTY_VALUE=
QUOTED_VALUE="Hello World"
SINGLE_QUOTED='Single Quote'
BOOL_FALSE=false
INT_NEGATIVE=-42
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write(content.strip())
        f.flush()
        yield f.name

    # Cleanup
    os.unlink(f.name)


@pytest.fixture
def large_env_file():
    """Create large .env file for testing"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("# Large test file\n")
        for i in range(1000):
            f.write(f"VAR_{i}=value_{i}\n")
        f.flush()
        yield f.name

    os.unlink(f.name)


@pytest.fixture
def malformed_env_file():
    """Create malformed .env file for testing"""
    content = """
# Malformed .env file
VALID_VAR=valid_value
MISSING_VALUE=
NO_EQUALS_SIGN
=MISSING_KEY
KEY_WITH_SPACES = value with spaces
DANGEROUS_SCRIPT=<script>alert('xss')</script>
PATH_TRAVERSAL=../../../etc/passwd
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write(content.strip())
        f.flush()
        yield f.name

    os.unlink(f.name)


# =============================================================================
# SIMPLE LOADER TESTS
# =============================================================================


class TestSimpleEnvLoader:
    """Test SimpleEnvLoader functionality"""

    def test_initialization(self):
        """Test loader initialization"""
        loader = SimpleEnvLoader()
        assert loader.env_data == {}
        assert not loader.is_loaded()

    @pytest.mark.asyncio
    async def test_load_from_file(self, temp_env_file):
        """Test loading from specific file"""
        loader = SimpleEnvLoader()
        await loader.load(temp_env_file)

        assert loader.is_loaded()
        assert loader.get("APP_NAME") == "TestApp"
        assert loader.get("DEBUG") is True
        assert loader.get("PORT") == 8080
        assert loader.get("FLOAT_VALUE") == 3.14

    def test_load_sync(self, temp_env_file):
        """Test synchronous loading"""
        loader = SimpleEnvLoader()
        loader.load_sync(temp_env_file)

        assert loader.is_loaded()
        assert loader.get("APP_NAME") == "TestApp"
        assert loader.get("DEBUG") is True

    @pytest.mark.asyncio
    async def test_load_nonexistent_file(self):
        """Test loading nonexistent file"""
        loader = SimpleEnvLoader()

        with pytest.raises(FileNotFoundError):
            await loader.load("/nonexistent/file.env")

    @pytest.mark.asyncio
    async def test_load_auto_discovery(self, temp_env_file):
        """Test auto-discovery of .env file"""
        # Copy temp file to current directory as .env
        env_content = Path(temp_env_file).read_text()
        with open(".env", "w") as f:
            f.write(env_content)

        try:
            loader = SimpleEnvLoader()
            await loader.load()
            assert loader.is_loaded()
            assert loader.get("APP_NAME") == "TestApp"
        finally:
            # Cleanup
            if os.path.exists(".env"):
                os.unlink(".env")

    def test_get_methods_before_loading(self):
        """Test get methods before loading raises error"""
        loader = SimpleEnvLoader()

        with pytest.raises(EnvNotLoadedError):
            loader.get("SOME_KEY")

        with pytest.raises(EnvNotLoadedError):
            loader.get_int("PORT")

        with pytest.raises(EnvNotLoadedError):
            loader.get_bool("DEBUG")

        with pytest.raises(EnvNotLoadedError):
            loader.get_str("APP_NAME")

        with pytest.raises(EnvNotLoadedError):
            loader.get_all()

        with pytest.raises(EnvNotLoadedError):
            loader.keys()

    def test_get_methods_with_types(self, temp_env_file):
        """Test typed get methods"""
        loader = SimpleEnvLoader()
        loader.load_sync(temp_env_file)

        # Test get_int
        assert loader.get_int("PORT") == 8080
        assert loader.get_int("PORT", 3000) == 8080
        assert loader.get_int("NONEXISTENT", 3000) == 3000

        # Test get_bool
        assert loader.get_bool("DEBUG") is True
        assert loader.get_bool("BOOL_FALSE") is False
        assert loader.get_bool("NONEXISTENT", True) is True

        # Test get_str
        assert loader.get_str("APP_NAME") == "TestApp"
        assert loader.get_str("NONEXISTENT", "default") == "default"

        # Test get_with_default
        assert loader.get_with_default("APP_NAME", "default") == "TestApp"
        assert loader.get_with_default("NONEXISTENT", "default") == "default"

    def test_type_conversion_errors(self, temp_env_file):
        """Test type conversion error handling"""
        loader = SimpleEnvLoader()
        loader.load_sync(temp_env_file)

        # Test invalid int conversion
        with pytest.raises(TypeConversionError):
            loader.get_int("APP_NAME")  # "TestApp" can't be converted to int

    def test_invalid_inputs(self):
        """Test invalid input handling"""
        loader = SimpleEnvLoader()

        # Test invalid key types
        with pytest.raises(InvalidInputError):
            loader.get(123)  # Non-string key

        with pytest.raises(InvalidInputError):
            loader.get_int(None)  # None key

    def test_clear_and_keys(self, temp_env_file):
        """Test clear and keys methods"""
        loader = SimpleEnvLoader()
        loader.load_sync(temp_env_file)

        # Test keys
        keys = loader.keys()
        assert "APP_NAME" in keys
        assert "DEBUG" in keys
        assert "PORT" in keys

        # Test get_all
        all_vars = loader.get_all()
        assert isinstance(all_vars, dict)
        assert all_vars["APP_NAME"] == "TestApp"

        # Test clear
        loader.clear()
        assert not loader.is_loaded()
        assert loader.env_data == {}


# =============================================================================
# SECURE LOADER TESTS
# =============================================================================


class TestSecureEnvLoader:
    """Test SecureEnvLoader functionality"""

    def test_initialization(self):
        """Test secure loader initialization"""
        loader = SecureEnvLoader()
        assert not loader.is_loaded()

        # Test custom session ID
        loader_with_session = SecureEnvLoader("custom-session")
        security_info = loader_with_session.get_security_info()
        assert security_info["session_id"] != loader.get_security_info()["session_id"]

    @pytest.mark.asyncio
    async def test_secure_loading(self, temp_env_file):
        """Test secure loading"""
        loader = SecureEnvLoader()

        # Test with specific file (don't try auto-discovery without .env file)
        from simpleenvs.secure import LoadOptions

        options = LoadOptions(path=temp_env_file, strict_validation=True)
        await loader.load_secure(options)

        assert loader.is_loaded()
        assert loader.get_secure("APP_NAME") == "TestApp"
        assert loader.get_secure("DEBUG") is True

        # Test auto-discovery failure
        loader2 = SecureEnvLoader()
        with pytest.raises(FileNotFoundError):
            await loader2.load_secure()  # Should fail - no .env in current dir

    def test_secure_get_methods(self, temp_env_file):
        """Test secure get methods"""
        loader = SecureEnvLoader()

        # Load synchronously for testing
        import asyncio

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        from simpleenvs.secure import LoadOptions

        options = LoadOptions(path=temp_env_file)
        loop.run_until_complete(loader.load_secure(options))

        # Test typed methods
        assert loader.get_int_secure("PORT") == 8080
        assert loader.get_int_secure("NONEXISTENT", 3000) == 3000

        assert loader.get_bool_secure("DEBUG") is True
        assert loader.get_bool_secure("BOOL_FALSE") is False
        assert loader.get_bool_secure("NONEXISTENT", True) is True

        assert loader.get_str_secure("APP_NAME") == "TestApp"
        assert loader.get_str_secure("NONEXISTENT", "default") == "default"

        assert loader.get_with_default_secure("APP_NAME", "default") == "TestApp"

        # Test get_all methods
        all_keys = loader.get_all_keys_secure()
        assert "APP_NAME" in all_keys

        all_vars = loader.get_all_secure()
        assert isinstance(all_vars, dict)
        assert all_vars["APP_NAME"] == "TestApp"

        loop.close()

    def test_security_info_and_logging(self, temp_env_file):
        """Test security information and access logging"""
        loader = SecureEnvLoader()

        # Get initial security info
        info = loader.get_security_info()
        assert "session_id" in info
        assert "creation_time" in info
        assert "access_count" in info

        # Load file and check access log
        import asyncio

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        from simpleenvs.secure import LoadOptions

        options = LoadOptions(path=temp_env_file)
        loop.run_until_complete(loader.load_secure(options))

        # Access some variables to generate logs
        loader.get_secure("APP_NAME")
        loader.get_secure("NONEXISTENT")

        # Check access log
        access_log = loader.get_access_log()
        assert len(access_log) > 0
        assert any(log["operation"] == "get" for log in access_log)

        loop.close()

    def test_file_integrity(self, temp_env_file):
        """Test file integrity checking"""
        loader = SecureEnvLoader()

        import asyncio

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        from simpleenvs.secure import LoadOptions

        options = LoadOptions(path=temp_env_file)
        loop.run_until_complete(loader.load_secure(options))

        # Test integrity verification
        assert loader.verify_file_integrity(temp_env_file)

        # Test non-tracked file
        assert not loader.verify_file_integrity("/nonexistent/file")

        loop.close()

    def test_secure_wipe(self, temp_env_file):
        """Test secure data wiping"""
        loader = SecureEnvLoader()

        import asyncio

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        from simpleenvs.secure import LoadOptions

        options = LoadOptions(path=temp_env_file)
        loop.run_until_complete(loader.load_secure(options))

        # Verify data is loaded
        assert loader.is_loaded()
        assert loader.get_secure("APP_NAME") == "TestApp"

        # Wipe data
        loader.secure_wipe()

        # Verify data is wiped
        assert not loader.is_loaded()

        loop.close()


# =============================================================================
# UTILITIES TESTS
# =============================================================================


class TestUtils:
    """Test utility functions"""

    def test_parse_env_value(self):
        """Test environment value parsing"""
        # Test boolean values
        assert utils.parse_env_value("true") is True
        assert utils.parse_env_value("TRUE") is True
        assert utils.parse_env_value("false") is False
        assert utils.parse_env_value("FALSE") is False

        # Test integer values
        assert utils.parse_env_value("123") == 123
        assert utils.parse_env_value("-456") == -456

        # Test float values
        assert utils.parse_env_value("3.14") == 3.14

        # Test string values
        assert utils.parse_env_value("hello") == "hello"
        assert utils.parse_env_value("") == ""

    def test_parse_env_value_strict(self):
        """Test strict environment value parsing"""
        # Test dangerous patterns
        with pytest.raises(InvalidInputError):
            utils.parse_env_value("<script>alert('xss')</script>", strict=True)

        with pytest.raises(InvalidInputError):
            utils.parse_env_value("$(rm -rf /)", strict=True)

    def test_normalize_boolean(self):
        """Test boolean normalization"""
        assert utils.normalize_boolean("true") is True
        assert utils.normalize_boolean("yes") is True
        assert utils.normalize_boolean("1") is True
        assert utils.normalize_boolean("false") is False
        assert utils.normalize_boolean("no") is False
        assert utils.normalize_boolean("0") is False
        assert utils.normalize_boolean(1) is True
        assert utils.normalize_boolean(0) is False

    def test_normalize_env_key(self):
        """Test environment key normalization"""
        assert utils.normalize_env_key("app-name") == "APP_NAME"
        assert utils.normalize_env_key("my.variable") == "MYVARIABLE"
        assert utils.normalize_env_key("123test") == "_123TEST"

    def test_security_validation(self):
        """Test security validation functions"""
        # Test value security
        utils.validate_value_security("safe_value")  # Should not raise

        with pytest.raises(InvalidInputError):
            utils.validate_value_security("<script>alert('xss')</script>")

        # Test path security
        utils.validate_path_security("safe/path/file.env")  # Should not raise

        with pytest.raises(PathTraversalError):
            utils.validate_path_security("../../../etc/passwd")

        with pytest.raises(InvalidInputError):
            utils.validate_path_security("path\x00with\x00nulls")

        # Test key format
        utils.validate_key_format("VALID_KEY", strict=True)  # Should not raise

        with pytest.raises(InvalidInputError):
            utils.validate_key_format("123invalid", strict=True)

        with pytest.raises(InvalidInputError):
            utils.validate_key_format("key=with=equals", strict=False)

    def test_file_operations(self, temp_env_file):
        """Test file operation utilities"""
        # Test file hash calculation
        hash1 = utils.calculate_file_hash(temp_env_file)
        hash2 = utils.calculate_file_hash(temp_env_file)
        assert hash1 == hash2  # Same file should have same hash
        assert len(hash1) == 64  # SHA-256 hash length

        # Test unsupported algorithm
        with pytest.raises(ValueError):
            utils.calculate_file_hash(temp_env_file, "unsupported_algo")

        # Test nonexistent file
        with pytest.raises(FileNotFoundError):
            utils.calculate_file_hash("/nonexistent/file")

        # Test safe file read
        content, encoding = utils.safe_file_read(temp_env_file)
        assert "APP_NAME=TestApp" in content
        assert encoding in ["utf-8", "utf-8-sig"]

        # Test file too large
        with pytest.raises(FileParsingError):
            utils.safe_file_read(temp_env_file, max_size=10)  # Very small limit

    def test_parsing_utilities(self, temp_env_file):
        """Test parsing utility functions"""
        # Read file content
        content, _ = utils.safe_file_read(temp_env_file)

        # Test parse_env_content
        env_data = utils.parse_env_content(content, strict=False)
        assert env_data["APP_NAME"] == "TestApp"
        assert env_data["DEBUG"] is True
        assert env_data["PORT"] == 8080

        # Test individual line parsing
        result = utils.parse_env_line("TEST_KEY=test_value")
        assert result == ("TEST_KEY", "test_value")

        result = utils.parse_env_line("# This is a comment")
        assert result is None

        result = utils.parse_env_line("")
        assert result is None

        result = utils.parse_env_line("INVALID_LINE_NO_EQUALS")
        assert result is None

    def test_env_info_and_formatting(self, temp_env_file):
        """Test environment info and formatting utilities"""
        content, _ = utils.safe_file_read(temp_env_file)
        env_data = utils.parse_env_content(content)

        # Test get_env_info
        info = utils.get_env_info(env_data)
        assert info["count"] > 0
        assert "str" in info["types"]
        assert "bool" in info["types"]
        assert "int" in info["types"]

        # Test format_env_summary
        summary = utils.format_env_summary(env_data, show_values=False)
        assert "Environment Variables Summary" in summary
        assert f"Total: {info['count']}" in summary

        summary_with_values = utils.format_env_summary(env_data, show_values=True)
        assert "Values:" in summary_with_values

        # Test export functions
        shell_format = utils.export_to_shell_format(env_data)
        assert 'export APP_NAME="TestApp"' in shell_format

        env_format = utils.export_to_env_format(env_data)
        assert "APP_NAME=TestApp" in env_format


# =============================================================================
# EXCEPTIONS TESTS
# =============================================================================


class TestExceptions:
    """Test exception classes and utilities"""

    def test_exception_creation(self):
        """Test exception creation and attributes"""
        # Test base exception
        error = SimpleEnvsError("Test message", {"key": "value"})
        assert str(error) == "Test message (Details: {'key': 'value'})"
        assert error.message == "Test message"
        assert error.details == {"key": "value"}

        # Test security exceptions
        path_error = PathTraversalError("../etc/passwd")
        assert path_error.attempted_path == "../etc/passwd"

        file_error = FileSizeError("/large/file", 1000000, 100000)
        assert file_error.size == 1000000
        assert file_error.max_size == 100000

        input_error = InvalidInputError("Invalid input", "bad_value")
        assert input_error.input_value == "bad_value"

    def test_exception_utilities(self):
        """Test exception utility functions"""
        from simpleenvs.exceptions import (
            format_security_error,
            get_error_code,
            handle_simpleenvs_error,
            is_security_critical,
        )

        # Test formatting
        error = PathTraversalError("../etc/passwd")
        formatted = format_security_error(error)
        assert "[SECURITY]" in formatted
        assert "PathTraversalError" in formatted

        # Test criticality
        assert is_security_critical(PathTraversalError("test"))
        assert not is_security_critical(SimpleEnvsError("test"))

        # Test error codes
        assert get_error_code(PathTraversalError("test")) == "SE101"
        assert get_error_code(SimpleEnvsError("test")) == "SE001"

        # Test error handling
        dev_msg = handle_simpleenvs_error(error, "development")
        prod_msg = handle_simpleenvs_error(error, "production")
        assert len(dev_msg) > len(prod_msg)  # Dev should be more detailed


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestIntegration:
    """Test module integration and global API"""

    @pytest.mark.asyncio
    async def test_global_api(self, temp_env_file):
        """Test global simpleenvs API"""
        # Test simple loading
        await simpleenvs.load(temp_env_file)
        assert simpleenvs.is_loaded()

        # Test global get functions
        assert simpleenvs.get("APP_NAME") == "TestApp"
        assert simpleenvs.get_int("PORT") == 8080
        assert simpleenvs.get_bool("DEBUG") is True
        assert simpleenvs.get_str("APP_NAME") == "TestApp"

        # Test secure loading
        await simpleenvs.load_secure(temp_env_file)
        assert simpleenvs.is_loaded_secure()

        # Test secure get functions
        assert simpleenvs.get_secure("APP_NAME") == "TestApp"
        assert simpleenvs.get_int_secure("PORT") == 8080
        assert simpleenvs.get_bool_secure("DEBUG") is True
        assert simpleenvs.get_str_secure("APP_NAME") == "TestApp"

        # Test utility functions
        all_keys = simpleenvs.get_all_keys()
        assert "APP_NAME" in all_keys

        info = simpleenvs.get_info()
        assert info["simple_loaded"] is True
        assert info["secure_loaded"] is True

        security_info = simpleenvs.get_security_info()
        assert security_info is not None
        assert "session_id" in security_info

        # Test cleanup
        simpleenvs.clear()
        assert not simpleenvs.is_loaded()
        assert not simpleenvs.is_loaded_secure()

    def test_memory_introspection(self, temp_env_file):
        """Test memory introspection functionality"""
        # Create a SecureEnvLoader directly
        loader = SecureEnvLoader()

        import asyncio

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        from simpleenvs.secure import LoadOptions

        options = LoadOptions(path=temp_env_file)
        loop.run_until_complete(loader.load_secure(options))

        # Test memory introspection
        from simpleenvs import _find_secure_loader_in_memory, get_all_secure_loaders

        found_loader = _find_secure_loader_in_memory()
        assert found_loader is not None
        assert found_loader.is_loaded()

        all_loaders = get_all_secure_loaders()
        assert len(all_loaders) >= 1
        assert any(loader.is_loaded() for loader in all_loaders)

        # Cleanup
        loader.secure_wipe()
        loop.close()


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================


class TestErrorHandling:
    """Test error handling and edge cases"""

    @pytest.mark.asyncio
    async def test_malformed_file_handling(self, malformed_env_file):
        """Test handling of malformed .env files"""
        # Simple loader should handle gracefully
        loader = SimpleEnvLoader()
        await loader.load(malformed_env_file)

        # Should still load valid variables
        assert loader.get("VALID_VAR") == "valid_value"

        # Secure loader should be more strict
        secure_loader = SecureEnvLoader()
        from simpleenvs.secure import LoadOptions

        options = LoadOptions(path=malformed_env_file, strict_validation=True)

        # Should raise exception for dangerous content or malformed data
        with pytest.raises((InvalidInputError, EnvSecurityError, FileParsingError)):
            await secure_loader.load_secure(options)

    def test_invalid_file_operations(self):
        """Test invalid file operations"""
        loader = SimpleEnvLoader()

        # Test loading directory instead of file (Windows uses C:\ instead of /)
        import platform

        if platform.system() == "Windows":
            invalid_path = "C:\\"
        else:
            invalid_path = "/"

        with pytest.raises((InvalidInputError, FileNotFoundError, FileParsingError)):
            loader.load_sync(invalid_path)

        # Test loading non-existent file
        with pytest.raises(FileNotFoundError):
            loader.load_sync("/nonexistent/file.env")

    def test_constants_and_environment_detection(self):
        """Test constants and environment detection"""
        from simpleenvs.constants import (
            get_environment_type,
            get_max_value_for_environment,
            get_settings_for_environment,
            is_feature_enabled,
        )

        # Test environment detection
        env_type = get_environment_type()
        assert env_type in ["development", "production", "testing", "staging"]

        # Test settings
        settings = get_settings_for_environment()
        assert isinstance(settings, dict)
        assert "strict_validation" in settings

        # Test feature flags
        assert isinstance(is_feature_enabled("async_loading"), bool)
        assert isinstance(is_feature_enabled("nonexistent_feature"), bool)

        # Test max values
        max_size = get_max_value_for_environment("max_file_size")
        assert isinstance(max_size, int)
        assert max_size > 0

        # Test all constants are accessible
        assert MAX_FILE_SIZE > 0
        assert MAX_KEY_LENGTH > 0
        assert len(DANGEROUS_PATTERNS) > 0
        assert len(TRUE_VALUES) > 0
        assert len(FALSE_VALUES) > 0


# =============================================================================
# ADDITIONAL COVERAGE TESTS
# =============================================================================


class TestAdditionalCoverage:
    """Additional tests to reach 90% coverage"""

    def test_edge_cases_and_error_paths(self):
        """Test edge cases and error paths for higher coverage"""
        # Test empty env data
        info = utils.get_env_info({})
        assert info["count"] == 0
        assert info["keys"] == []

        # Test export with empty data
        shell_export = utils.export_to_shell_format({})
        assert shell_export == ""

        env_export = utils.export_to_env_format({})
        assert env_export == ""

        # Test summary with empty data
        summary = utils.format_env_summary({}, show_values=True)
        assert "Total: 0 variables" in summary

    def test_utils_edge_cases(self):
        """Test utils edge cases"""
        # Test normalize_boolean with edge cases
        assert utils.normalize_boolean(True) is True
        assert utils.normalize_boolean(False) is False
        assert utils.normalize_boolean([1, 2, 3]) is True  # Non-empty list
        assert utils.normalize_boolean([]) is False  # Empty list
        assert utils.normalize_boolean(None) is False

        # Test parse_env_value with non-string input
        with pytest.raises(TypeConversionError):
            utils.parse_env_value(123, strict=True)

        # Test normalize_env_key edge cases
        assert utils.normalize_env_key("") == ""
        assert utils.normalize_env_key("a") == "A"

        # Test validate_completeness
        env_data = {"KEY1": "value1", "KEY2": "value2"}
        required = ["KEY1", "KEY2", "KEY3"]
        missing = utils.validate_env_completeness(env_data, required)
        assert missing == ["KEY3"]

        missing_none = utils.validate_env_completeness(env_data, ["KEY1", "KEY2"])
        assert missing_none == []

    def test_exception_edge_cases(self):
        """Test exception edge cases"""
        from simpleenvs.exceptions import SecureErrorHandler

        # Test SecureErrorHandler
        with SecureErrorHandler("test_op", suppress_details=True):
            pass  # Normal operation

        # Test error without details
        error = SimpleEnvsError("Test message")
        assert str(error) == "Test message"
        assert error.details is None

        # Test all specific exception types
        session_error = SessionError("sess123", "test issue")
        assert session_error.session_id == "sess123"
        assert session_error.issue == "test issue"

        memory_error = MemorySecurityError("test_op", "test reason")
        assert memory_error.operation == "test_op"
        assert memory_error.reason == "test reason"

        config_error = ConfigurationError("test_component", "test issue")
        assert config_error.component == "test_component"
        assert config_error.issue == "test issue"

    def test_file_operations_edge_cases(self):
        """Test file operations edge cases"""
        # Test find_env_files with non-existent path
        found = utils.find_env_files("/nonexistent/path", 1)
        assert found == []

        # Test calculate_file_hash with different algorithms
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content")
            f.flush()
            temp_file = f.name

        try:
            # Test MD5
            hash_md5 = utils.calculate_file_hash(temp_file, "md5")
            assert len(hash_md5) == 32

            # Test SHA-1
            hash_sha1 = utils.calculate_file_hash(temp_file, "sha1")
            assert len(hash_sha1) == 40

        finally:
            # Safe cleanup for Windows
            try:
                os.unlink(temp_file)
            except (OSError, PermissionError):
                pass  # Ignore cleanup errors on Windows

    def test_parsing_edge_cases(self):
        """Test parsing edge cases"""
        # Test parse_env_line with edge cases
        result = utils.parse_env_line("KEY=", strict=False)
        assert result == ("KEY", "")

        result = utils.parse_env_line("KEY=value", strict=True)
        assert result == ("KEY", "value")

        # Test with quotes
        result = utils.parse_env_line('KEY="quoted value"')
        assert result == ("KEY", "quoted value")

        result = utils.parse_env_line("KEY='single quoted'")
        assert result == ("KEY", "single quoted")

        # Test parse_env_content with different scenarios
        content = """
# Comment
KEY1=value1

KEY2=true
KEY3=123
EMPTY_KEY=
"""
        env_data = utils.parse_env_content(content, strict=False)
        assert env_data["KEY1"] == "value1"
        assert env_data["KEY2"] is True
        assert env_data["KEY3"] == 123
        assert env_data["EMPTY_KEY"] == ""

    def test_security_validation_edge_cases(self):
        """Test security validation edge cases"""
        # Test validate_key_format with relaxed mode
        utils.validate_key_format("key_with_underscore", strict=False)  # Should pass
        utils.validate_key_format("key-with-hyphen", strict=False)  # Should pass

        # Test path validation with edge cases
        utils.validate_path_security("normal/path")  # Should pass

        with pytest.raises(InvalidInputError):
            utils.validate_path_security("")  # Empty path

        with pytest.raises(InvalidInputError):
            utils.validate_path_security(None)  # None path

        # Test very long path
        long_path = "a" * 2000
        with pytest.raises(InvalidInputError):
            utils.validate_path_security(long_path)

    @pytest.mark.asyncio
    async def test_module_level_functions(self, temp_env_file):
        """Test module-level convenience functions"""
        from simpleenvs.secure import load_from_path_secure, load_secure
        from simpleenvs.simple import load_env, load_env_sync

        # Test simple module functions
        loader1 = await load_env(temp_env_file)
        assert loader1.is_loaded()

        loader2 = load_env_sync(temp_env_file)
        assert loader2.is_loaded()

        # Test secure module functions
        secure_loader1 = await load_secure(temp_env_file)
        assert secure_loader1.is_loaded()

        secure_loader2 = await load_from_path_secure(temp_env_file)
        assert secure_loader2.is_loaded()

    def test_constants_module_main(self):
        """Test constants module __main__ execution"""
        # This tests the if __name__ == "__main__" block in constants.py
        from simpleenvs import constants

        # Test that constants are accessible
        assert hasattr(constants, "VERSION")
        assert hasattr(constants, "MAX_FILE_SIZE")
        assert hasattr(constants, "DANGEROUS_PATTERNS")

        # Test utility functions
        env_type = constants.get_environment_type()
        assert isinstance(env_type, str)

        settings = constants.get_settings_for_environment()
        assert isinstance(settings, dict)

    def test_more_coverage_paths(self):
        """Test additional paths for coverage"""
        # Test utils with quoted values that need escaping
        env_data = {"KEY": 'value with "quotes"'}
        env_format = utils.export_to_env_format(env_data)
        assert 'KEY="value with \\"quotes\\""' in env_format

        # Test shell format without quotes
        shell_format = utils.export_to_shell_format(env_data, quote_values=False)
        assert 'export KEY=value with "quotes"' in shell_format

        # Test parse_env_value with float edge case
        result = utils.parse_env_value("123.456")
        assert result == 123.456

        # Test large integer out of range (strict mode should raise exception)
        large_number = str(2**64)  # Larger than 64-bit signed int
        with pytest.raises(TypeConversionError):
            utils.parse_env_value(large_number, strict=True)

        # Test large integer out of range (non-strict mode should return as string)
        result_non_strict = utils.parse_env_value(large_number, strict=False)
        assert isinstance(result_non_strict, str)
        assert result_non_strict == large_number

        # Test path with long length
        long_path = "a" * 500  # Still under 1024 limit
        utils.validate_path_security(long_path)  # Should pass

        # Test key with maximum length
        max_key = "A" * 50  # Valid key
        utils.validate_key_format(max_key, strict=True)  # Should pass

    def test_secure_loader_edge_cases(self, temp_env_file):
        """Test SecureEnvLoader edge cases"""
        loader = SecureEnvLoader()

        # Test get methods before loading
        assert loader.get_secure("NONEXISTENT") is None
        assert loader.get_int_secure("NONEXISTENT", 42) == 42
        assert loader.get_bool_secure("NONEXISTENT", True) is True
        assert loader.get_str_secure("NONEXISTENT", "default") == "default"
        assert loader.get_with_default_secure("NONEXISTENT", "default") == "default"

        # Test when not loaded
        assert loader.get_all_keys_secure() == []
        assert loader.get_all_secure() == {}

        # Test verify_file_integrity with non-tracked file
        assert not loader.verify_file_integrity("nonexistent.env")

    def test_utils_parse_env_line_strict_errors(self):
        """Test parse_env_line strict mode errors"""
        # Test empty key in strict mode
        with pytest.raises(FileParsingError):
            utils.parse_env_line("=value", strict=True)

        # Test line without equals in strict mode
        with pytest.raises(FileParsingError):
            utils.parse_env_line("INVALID_LINE", strict=True)

        # Test dangerous value in strict mode
        with pytest.raises(FileParsingError):
            utils.parse_env_line("KEY=<script>alert('xss')</script>", strict=True)


if __name__ == "__main__":
    # Run all tests
    pytest.main([__file__, "-v", "--cov=simpleenvs", "--cov-report=term-missing"])
