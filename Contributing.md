# Contributing to SimpleEnvs-Python

Thank you for your interest in contributing to SimpleEnvs! 🎉

We welcome contributions from developers of all skill levels. Whether you're fixing a bug, adding a feature, improving documentation, or just asking questions, your involvement helps make SimpleEnvs better for everyone.

## 🚀 Quick Start

1. **Fork** the repository on GitHub
2. **Clone** your fork locally
3. **Create** a new branch for your changes
4. **Make** your changes
5. **Test** your changes
6. **Submit** a pull request

## 🛠️ Development Setup

### Prerequisites

- Python 3.7+
- Git
- A code editor (VS Code, PyCharm, etc.)

### Local Development

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/SimpleEnvs-Python.git
cd SimpleEnvs-Python

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install test dependencies
pip install -e ".[test]"

# Run tests to verify setup
pytest tests/ -v
```

### Development Dependencies

The development environment includes:
- `pytest` - Testing framework
- `black` - Code formatting
- `isort` - Import sorting
- `mypy` - Type checking
- `flake8` - Linting
- `coverage` - Test coverage

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=simpleenvs --cov-report=html

# Run specific test file
pytest tests/test_simple.py -v

# Run tests with specific Python version
python3.9 -m pytest tests/
```

### Writing Tests

- Place test files in the `tests/` directory
- Name test files with `test_*.py` pattern
- Use descriptive test function names: `test_load_dotenv_with_missing_file()`
- Include both positive and negative test cases
- Test edge cases and error conditions

Example test:

```python
import pytest
from simpleenvs import load_dotenv, get_str

def test_load_dotenv_with_custom_path():
    """Test loading .env file from custom path"""
    # Setup
    test_env_content = "TEST_VAR=test_value\nDEBUG=true"
    
    # Test
    with open("test.env", "w") as f:
        f.write(test_env_content)
    
    load_dotenv("test.env")
    
    # Assert
    assert get_str("TEST_VAR") == "test_value"
    
    # Cleanup
    os.remove("test.env")
```

### Performance Testing

```bash
# Run benchmarks
python -m simpleenvs.benchmark

# Compare with python-dotenv
python benchmark.py --compare
```

## 🎯 Types of Contributions

### 🐛 Bug Reports

Before submitting a bug report:
- Check existing issues to avoid duplicates
- Use the latest version of SimpleEnvs
- Include a minimal reproducible example

**Bug Report Template:**
```markdown
**Description:**
A clear description of the bug.

**Steps to Reproduce:**
1. Create .env file with...
2. Run the following code...
3. Expected vs actual behavior

**Environment:**
- Python version: 
- SimpleEnvs version:
- Operating System:

**Code Example:**
```python
# Minimal code that reproduces the issue
```

### ✨ Feature Requests

We love new ideas! When proposing features:
- Explain the use case and benefit
- Consider backward compatibility
- Provide implementation ideas if possible

**Feature Request Template:**
```markdown
**Feature Description:**
What you'd like to see implemented.

**Use Case:**
Why this feature would be valuable.

**Proposed API:**
```python
# How you envision using this feature
```

**Implementation Ideas:**
Any thoughts on how this could be implemented.
```

### 📚 Documentation

Documentation improvements are always welcome:
- Fix typos and grammatical errors
- Improve code examples
- Add missing docstrings
- Update README.md
- Create tutorials or guides

### 🔧 Code Contributions

#### Coding Standards

- **Code Style**: We use `black` for formatting and `isort` for import sorting
- **Type Hints**: All public functions should have type hints
- **Docstrings**: Use Google-style docstrings for all public functions
- **Error Handling**: Provide meaningful error messages
- **Security**: Follow security best practices

#### Before You Code

1. **Check existing issues** - Someone might already be working on it
2. **Open an issue** - Discuss your approach before major changes
3. **Create a branch** - Use descriptive branch names: `feature/auto-reload` or `fix/windows-path-issue`

#### Code Review Process

1. All submissions require review before merging
2. We may ask for changes to align with project goals
3. Please be patient - reviews take time
4. Address feedback promptly

## 🔒 Security

### Reporting Security Issues

**Do not open public issues for security vulnerabilities.**

Instead, email security concerns to: **[security email to be added]**

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Security Guidelines

- Never commit sensitive data (API keys, passwords, etc.)
- Use `load_dotenv_secure()` for sensitive environment variables
- Follow OWASP security principles
- Validate all inputs
- Handle errors securely

## 🎨 Code Style Guide

### Python Style

We follow PEP 8 with these additional guidelines:

```python
# Good: Clear function names
def load_environment_variables(file_path: str) -> None:
    """Load environment variables from file."""
    pass

# Good: Type hints
def get_secure_value(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get secure environment variable with type safety."""
    pass

# Good: Docstrings
def parse_env_file(file_path: str) -> Dict[str, str]:
    """
    Parse .env file and return key-value pairs.
    
    Args:
        file_path: Path to the .env file
        
    Returns:
        Dictionary of environment variables
        
    Raises:
        FileNotFoundError: If file doesn't exist
        SecurityError: If file contains dangerous patterns
    """
    pass
```

### Formatting

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Type check
mypy src/

# Lint
flake8 src/ tests/
```

## 📋 Pull Request Process

### Before Submitting

- [ ] Code is formatted with `black` and `isort`
- [ ] All tests pass: `pytest tests/`
- [ ] Type checking passes: `mypy src/`
- [ ] No linting errors: `flake8 src/ tests/`
- [ ] Documentation is updated if needed
- [ ] CHANGELOG.md is updated for significant changes

### Pull Request Template

```markdown
**Description:**
Brief description of changes made.

**Type of Change:**
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

**Testing:**
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] Manual testing completed

**Checklist:**
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)

**Related Issues:**
Fixes #123
```

## 🌟 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes for significant contributions
- Given credit in documentation where appropriate

## 🤝 Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment:

- **Be respectful** - Treat everyone with kindness and respect
- **Be collaborative** - Work together constructively
- **Be patient** - Help others learn and grow
- **Be inclusive** - Welcome people of all backgrounds and experience levels

### Getting Help

- **GitHub Issues** - For bugs and feature requests
- **GitHub Discussions** - For questions and general discussion
- **Code Reviews** - Learn from feedback and help others improve

## 🚀 Advanced Contributing

### Performance Contributions

When improving performance:
- Include benchmark results
- Test with various file sizes
- Consider memory usage impact
- Maintain backward compatibility

### Security Contributions

When working on security features:
- Follow secure coding practices
- Include security test cases
- Document security implications
- Consider threat modeling

### AI Collaboration

This project was built using AI collaboration techniques. We welcome:
- Improvements to AI-human collaboration workflows
- Documentation of AI-assisted development processes
- Sharing of effective prompting strategies

## 📞 Contact

- **Project Maintainer**: @vmintf
- **General Questions**: Open a GitHub Discussion
- **Security Issues**: vmintf@gmail.com
- **Documentation Issues**: Open a GitHub Issue

## 🙏 Thank You

Every contribution, no matter how small, makes SimpleEnvs better. Thank you for being part of our community!

---

**Happy Coding!** 🚀

*SimpleEnvs-Python - Making environment variable management simple, secure, and fast.*