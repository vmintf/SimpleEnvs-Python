# SimpleEnvs Documentation

Welcome to SimpleEnvs - the ultra-secure, high-performance .env file loader for Python!

```{eval-rst}
.. |version| replace:: |release|

.. image:: https://badge.fury.io/py/simpleenvs-python.svg
   :target: https://badge.fury.io/py/simpleenvs-python
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/simpleenvs-python.svg
   :target: https://pypi.org/project/simpleenvs-python/
   :alt: Python versions

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://github.com/vmintf/SimpleEnvs-Python/blob/main/LICENSE
   :alt: License

.. image:: https://img.shields.io/badge/version-|release|-blue.svg
   :target: https://github.com/vmintf/SimpleEnvs-Python/releases
   :alt: Current Version
```

## 🚀 Why SimpleEnvs?

SimpleEnvs is a **drop-in replacement** for python-dotenv with proven improvements:

- 🏃‍♂️ **2-4x faster** loading performance
- 🔒 **Enterprise-grade security** with memory isolation  
- 🎯 **Automatic type conversion** (int, bool, float)
- 💾 **Memory efficient** with optimized parsing
- ⚡ **Zero configuration** - works out of the box
- 🔄 **100% python-dotenv compatible** API

## ⚡ Quick Example

```python
# Create .env file
echo "APP_NAME=MyApp\nDEBUG=true\nPORT=8080" > .env

# Load environment variables (just like python-dotenv!)
from simpleenvs import load_dotenv
load_dotenv()

# Access variables
import os
print(os.getenv('APP_NAME'))  # "MyApp"
print(os.getenv('DEBUG'))     # "True"
print(os.getenv('PORT'))      # "8080"
```

## 🔒 Security Mode

For sensitive data that should never touch `os.environ`:

```python
from simpleenvs import load_dotenv_secure, get_secure

# Load with maximum security (memory-isolated)
load_dotenv_secure()

# Access secure variables (NOT in os.environ!)
jwt_secret = get_secure('JWT_SECRET')
db_password = get_secure('DB_PASSWORD')

# Verify security
import os
print(os.getenv('JWT_SECRET'))  # None - properly isolated! 🔒
```

## 📊 Performance

Consistent 2-4x performance improvements over python-dotenv:

| Variables | SimpleEnvs | python-dotenv | **Speedup** |
|-----------|------------|---------------|-------------|
| 100 vars  | 2.17ms     | 8.04ms        | **3.7x faster** ⚡ |
| 500 vars  | 14.3ms     | 43.1ms        | **3.0x faster** ⚡ |
| 1000 vars | 43.4ms     | 102ms         | **2.4x faster** ⚡ |

## 📚 Documentation

```{toctree}
:maxdepth: 2
:caption: Contents:

installation
quickstart
api-reference
security
```

## 🔗 Links

- 📦 [PyPI Package](https://pypi.org/project/simpleenvs-python/)
- 🐛 [Issue Tracker](https://github.com/vmintf/SimpleEnvs-Python/issues)
- 💬 [Discussions](https://github.com/vmintf/SimpleEnvs-Python/discussions)
- 📧 [Contact](mailto:vmintf@gmail.com)

## 📄 License

MIT License - see [LICENSE](https://github.com/vmintf/SimpleEnvs-Python/blob/main/LICENSE) file for details.

---

**Ready to get started?** Check out the [Installation Guide](installation.md)! 🎉