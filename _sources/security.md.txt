# Security Guide

SimpleEnvs provides enterprise-grade security features to protect your sensitive environment variables and prevent common attack vectors.

## Table of Contents

- [Security Overview](#security-overview)
- [Simple vs Secure Mode](#simple-vs-secure-mode)
- [Memory Isolation](#memory-isolation)
- [Input Validation](#input-validation)
- [File Security](#file-security)
- [Path Traversal Protection](#path-traversal-protection)
- [Integrity Checking](#integrity-checking)
- [Access Logging](#access-logging)
- [Security Best Practices](#security-best-practices)
- [Threat Model](#threat-model)
- [Compliance](#compliance)

---

## Security Overview

SimpleEnvs implements a **defense-in-depth** security model with multiple layers of protection:

```
🛡️ Defense Layers
├── Input Validation      → Prevent injection attacks
├── Path Security        → Block traversal attacks  
├── Memory Isolation     → Isolate sensitive data
├── File Integrity      → Detect tampering
├── Access Logging      → Monitor usage
└── Secure Cleanup      → Prevent data leaks
```

## Simple vs Secure Mode

### Simple Mode (Default)
Perfect for development and most production use cases:

```python
from simpleenvs import load_dotenv
load_dotenv()  # Variables stored in os.environ
```

**Security Features:**
- ✅ Input validation
- ✅ Path traversal protection
- ✅ File size limits
- ❌ Memory isolation
- ❌ Access logging

### Secure Mode (Enterprise)
Memory-isolated environment variables that never touch `os.environ`:

```python
from simpleenvs import load_dotenv_secure, get_secure

load_dotenv_secure()  # Memory-isolated loading

# Secure access (not in os.environ!)
jwt_secret = get_secure('JWT_SECRET')
db_password = get_secure('DB_PASSWORD')

# Verify isolation
import os
print(os.getenv('JWT_SECRET'))  # None - properly isolated! 🔒
```

**Security Features:**
- ✅ All Simple Mode features
- ✅ **Memory isolation**
- ✅ **Access logging**
- ✅ **Session tracking**
- ✅ **Integrity verification**
- ✅ **Secure cleanup**

---

## Memory Isolation

### The Problem

Traditional environment loaders store secrets in `os.environ`, making them visible to:
- All processes in the system
- Subprocess calls
- Process inspection tools
- Memory dumps
- Third-party libraries

### SimpleEnvs Solution

Secure mode keeps sensitive data in **memory-isolated storage**:

```python
import simpleenvs
import os

# Load sensitive data securely
simpleenvs.load_dotenv_secure()

# Access through secure API
api_key = simpleenvs.get_secure('API_KEY')
db_password = simpleenvs.get_secure('DATABASE_PASSWORD')

# ✅ Data is accessible through SimpleEnvs
print(f"API Key loaded: {api_key is not None}")

# 🔒 Data is NOT in system environment
assert os.getenv('API_KEY') is None
assert os.getenv('DATABASE_PASSWORD') is None

# 🔒 Not visible to subprocesses
import subprocess
result = subprocess.run(['env'], capture_output=True, text=True)
assert 'API_KEY' not in result.stdout
```

### Memory Protection Features

1. **Private Storage**: Uses Python's name mangling (`__env_data`)
2. **Weak References**: Automatic cleanup when loader is destroyed
3. **Secure Wipe**: Multiple-pass overwriting of sensitive data
4. **Isolation**: No cross-contamination between loaders

---

## Input Validation

### Dangerous Pattern Detection

SimpleEnvs automatically detects and blocks dangerous patterns:

```python
# .env file with dangerous content
"""
SAFE_VAR=hello_world
DANGEROUS_VAR=$(cat /etc/passwd)
SCRIPT_VAR=<script>alert('xss')</script>
"""
```

```python
import simpleenvs

try:
    # Strict mode (recommended for production)
    await simpleenvs.load_secure(strict=True)
except simpleenvs.InvalidInputError as e:
    print(f"Blocked dangerous pattern: {e}")
```

**Detected Patterns:**
- Command injection: `$(`, `` ` ``, `${`
- Script injection: `<script>`, `javascript:`
- Code execution: `eval(`, `exec(`, `__import__`
- System access: `subprocess`, `os.system`

### Key Validation

Environment variable keys must follow secure naming conventions:

```python
# ✅ Valid keys
APP_NAME=MyApp          # Alphanumeric + underscore
API_KEY=secret         # Starts with letter
DB_HOST_1=localhost    # Numbers allowed

# ❌ Invalid keys (blocked in strict mode)
123_INVALID=value      # Cannot start with number
APP-NAME=value         # Hyphens only in relaxed mode
KEY WITH SPACES=value  # Spaces not allowed
KEY=WITH=EQUALS=value  # Multiple equals signs
```

### Value Length Limits

Prevents buffer overflow and DoS attacks:

- **Keys**: Maximum 128 characters
- **Values**: Maximum 1,024 characters  
- **Lines**: Maximum 4,096 characters
- **Files**: Maximum 10MB

---

## File Security

### File Type Validation

Only text files are accepted:

```python
# ✅ Allowed files
.env
.env.production
config.txt
settings.conf

# ❌ Blocked files
malicious.exe
script.sh
binary.jpg
```

### Symbolic Link Protection

Prevents symbolic link attacks:

```python
# Create malicious symlink
# ln -s /etc/passwd .env

try:
    simpleenvs.load_dotenv_secure()
except simpleenvs.InvalidInputError:
    print("Symbolic link blocked!")
```

### File Size Limits

Prevents resource exhaustion:

```python
# Environment-specific limits
Production:  8MB (80% of base limit)
Testing:     5MB (50% of base limit)  
Development: 10MB (100% of base limit)
```

---

## Path Traversal Protection

### Attack Prevention

SimpleEnvs blocks all path traversal attempts:

```python
# ❌ Blocked attempts
simpleenvs.load_dotenv('../../../etc/passwd')
simpleenvs.load_dotenv('..\\..\\windows\\system32\\config')
simpleenvs.load_dotenv('/absolute/path/attack')
simpleenvs.load_dotenv('path/with/null\x00byte')
```

**Protected Patterns:**
- `..` (directory traversal)
- Null bytes (`\x00`)
- Absolute paths (`/`, `C:\`)
- URL encoding (`%2e%2e`)
- Unicode variations

### Safe Directory Scanning

Auto-discovery only searches safe locations:

```python
# ✅ Safe directories
./
./config/
./environments/
./settings/

# ❌ Excluded directories
__pycache__/
.git/
node_modules/
.venv/
build/
dist/
```

---

## Integrity Checking

### File Hash Verification

Secure mode automatically calculates and stores file hashes:

```python
from simpleenvs import SecureEnvLoader

loader = SecureEnvLoader()
await loader.load_secure()

# Verify file hasn't been tampered with
is_valid = loader.verify_file_integrity('.env')
if not is_valid:
    print("⚠️ File may have been modified!")
```

### Hash Algorithm

- **Algorithm**: SHA-256
- **Storage**: In-memory only
- **Verification**: On-demand or periodic

### Tamper Detection

```python
import simpleenvs

# Initial load
simpleenvs.load_dotenv_secure()

# ... time passes, file might be modified ...

# Check integrity
try:
    security_info = simpleenvs.get_security_info()
    # Verify using stored hash
except simpleenvs.IntegrityError as e:
    print(f"File tampered: {e.file_path}")
    print(f"Expected: {e.expected_hash}")
    print(f"Actual: {e.actual_hash}")
```

---

## Access Logging

### Security Monitoring

Secure mode logs all access attempts for security auditing:

```python
from simpleenvs import SecureEnvLoader

loader = SecureEnvLoader()
await loader.load_secure()

# Access some variables
api_key = loader.get_secure('API_KEY')
db_url = loader.get_secure('DATABASE_URL')

# Review access log
access_log = loader.get_access_log()
for entry in access_log:
    print(f"{entry['timestamp']}: {entry['operation']} - {entry['key']}")
```

### Log Entry Format

```python
{
    "timestamp": 1640995200.0,
    "session_id": "a1b2c3d4e5f6",
    "operation": "get",
    "key": "API_KEY", 
    "success": True,
    "access_count": 15
}
```

### Logged Operations

- `load` - File loading
- `get` - Variable access
- `path_validation` - Path security checks
- `file_parse` - File parsing
- `integrity_check` - Hash verification

### Session Tracking

Each SecureEnvLoader instance has a unique session:

```python
loader = SecureEnvLoader(session_id="prod-001")
security_info = loader.get_security_info()

print(f"Session ID: {security_info['session_id']}")
print(f"Created: {security_info['creation_time']}")
print(f"Access Count: {security_info['access_count']}")
```

---

## Security Best Practices

### 1. Use Secure Mode for Sensitive Data

```python
# ✅ Recommended: Separate public and private config
import simpleenvs

# Public configuration (can be in os.environ)
await simpleenvs.load('config.env')
app_name = simpleenvs.get_str('APP_NAME')

# Sensitive secrets (memory-isolated)
await simpleenvs.load_secure('secrets.env')
jwt_secret = simpleenvs.get_secure('JWT_SECRET')
```

### 2. Enable Strict Validation in Production

```python
# Production configuration
import os
env = os.getenv('ENVIRONMENT', 'development')

if env == 'production':
    # Maximum security
    await simpleenvs.load_secure(strict=True)
else:
    # Development flexibility
    await simpleenvs.load(strict=False)
```

### 3. Implement Required Variable Checks

```python
def validate_environment():
    """Validate all required environment variables are present"""
    required_vars = [
        'DATABASE_URL',
        'JWT_SECRET', 
        'API_KEY',
        'SMTP_PASSWORD'
    ]
    
    missing = []
    for var in required_vars:
        if not simpleenvs.get_secure(var):
            missing.append(var)
    
    if missing:
        raise ValueError(f"Missing required variables: {missing}")

# Call during application startup
validate_environment()
```

### 4. Regular Security Audits

```python
def security_audit():
    """Perform security audit of environment configuration"""
    info = simpleenvs.get_security_info()
    
    # Check access patterns
    if info['access_count'] > 1000:
        print("⚠️ High access count - investigate")
    
    # Verify loader integrity
    loaders = simpleenvs.get_all_secure_loaders()
    for loader in loaders:
        if not loader.verify_file_integrity('.env'):
            print("⚠️ File integrity compromised")

# Run periodically
security_audit()
```

### 5. Secure Cleanup

```python
import atexit
import simpleenvs

def cleanup_secrets():
    """Securely wipe sensitive data on exit"""
    try:
        simpleenvs.clear()
        print("✅ Secrets cleaned up")
    except Exception as e:
        print(f"⚠️ Cleanup error: {e}")

# Register cleanup handler
atexit.register(cleanup_secrets)
```

### 6. Environment-Specific Configuration

```python
import simpleenvs

class SecureConfig:
    def __init__(self):
        env = simpleenvs.get_environment_type()
        
        if env == 'production':
            # Maximum security settings
            self.strict_validation = True
            self.require_integrity_check = True
            self.log_access = True
            
        elif env == 'development':
            # Development convenience
            self.strict_validation = False
            self.require_integrity_check = False
            self.log_access = False
            
        self.load_environment()
    
    def load_environment(self):
        options = LoadOptions(
            strict_validation=self.strict_validation
        )
        await simpleenvs.load_secure(options)
```

---

## Threat Model

### Protected Against

| Attack Vector | Protection | Implementation |
|---------------|------------|----------------|
| **Code Injection** | Input validation | Pattern detection |
| **Path Traversal** | Path validation | Traversal blocking |
| **Data Exposure** | Memory isolation | Private storage |
| **File Tampering** | Integrity checks | SHA-256 hashing |
| **Privilege Escalation** | Access controls | Permission validation |
| **Resource Exhaustion** | Size limits | Configurable limits |
| **Information Leakage** | Secure cleanup | Memory wiping |

### Not Protected Against

⚠️ **Important limitations:**

- **Physical access** to the machine
- **Root/Administrator** privilege escalation
- **Memory dumps** by privileged processes
- **Debugger attachment** by system admin
- **Side-channel attacks** (timing, power analysis)
- **Social engineering** attacks

### Assumptions

SimpleEnvs security model assumes:
- Application runs in **trusted environment**
- System is **not compromised** at OS level
- Python interpreter is **secure and trusted**
- File system has **basic access controls**

---

## Compliance

### Industry Standards

SimpleEnvs helps meet various compliance requirements:

**OWASP Top 10:**
- ✅ A03 - Injection (Input validation)
- ✅ A01 - Broken Access Control (Memory isolation)
- ✅ A09 - Security Logging (Access monitoring)

**NIST Cybersecurity Framework:**
- ✅ Identify - Asset inventory (environment variables)
- ✅ Protect - Access controls (secure mode)
- ✅ Detect - Monitoring (access logs)
- ✅ Respond - Incident handling (integrity checks)

### Security Certifications

While not certified, SimpleEnvs implements security practices aligned with:
- **ISO 27001** - Information Security Management
- **SOC 2 Type II** - Security controls
- **PCI DSS** - Data protection (for payment systems)

### Audit Trail

For compliance auditing, SecureEnvLoader provides:

```python
def generate_audit_report():
    """Generate compliance audit report"""
    info = simpleenvs.get_security_info()
    access_log = simpleenvs.get_access_log()
    
    report = {
        'session_id': info['session_id'],
        'total_accesses': info['access_count'],
        'security_events': [
            entry for entry in access_log 
            if not entry['success']
        ],
        'file_integrity': 'verified',
        'memory_isolation': 'enabled'
    }
    
    return report
```

---

## Security Configuration

### Environment-Specific Settings

```python
# Production (Maximum Security)
ENVIRONMENT=production
SIMPLEENVS_STRICT_VALIDATION=true
SIMPLEENVS_REQUIRE_INTEGRITY=true
SIMPLEENVS_LOG_ACCESS=true

# Development (Balanced)
ENVIRONMENT=development  
SIMPLEENVS_STRICT_VALIDATION=false
SIMPLEENVS_REQUIRE_INTEGRITY=false
SIMPLEENVS_LOG_ACCESS=false
```

### Runtime Configuration

```python
from simpleenvs.secure import LoadOptions

# Custom security configuration
options = LoadOptions(
    path='.env.production',
    max_depth=1,  # Restrict search depth
    strict_validation=True  # Enable all validations
)

await simpleenvs.load_secure(options)
```

---

## Incident Response

### Security Event Detection

```python
def monitor_security_events():
    """Monitor for security incidents"""
    access_log = simpleenvs.get_access_log()
    
    # Check for failed access attempts
    failed_attempts = [
        entry for entry in access_log[-10:]  # Last 10 entries
        if not entry['success']
    ]
    
    if len(failed_attempts) > 5:
        alert_security_team("Multiple failed access attempts detected")
    
    # Check for unusual access patterns
    recent_keys = [entry['key'] for entry in access_log[-50:]]
    if len(set(recent_keys)) > 20:  # Accessing many different keys
        alert_security_team("Unusual access pattern detected")

def alert_security_team(message):
    """Alert security team of potential incident"""
    print(f"🚨 SECURITY ALERT: {message}")
    # Implement your alerting mechanism here
```

### Recovery Procedures

1. **Isolate the affected system**
2. **Review access logs** for unauthorized access
3. **Verify file integrity** of environment files
4. **Rotate compromised secrets** immediately
5. **Update security policies** if needed

---

## Advanced Security Features

### Cross-Module Access

SimpleEnvs automatically enables secure environment variables loaded in one module to be accessed from other modules without re-loading, while maintaining full memory isolation.

#### Automatic Discovery

When you load secure environment variables in a parent module, child modules can automatically access the same data:

```python
# main.py (parent module)
import simpleenvs

async def startup():
    # Load secrets once in main module
    await simpleenvs.load_secure('.env.production')
    print("✅ Secrets loaded in main module")

# database.py (child module)
import simpleenvs

class DatabaseConfig:
    def __init__(self):
        # Automatically finds SecureEnvLoader from main.py!
        self.url = simpleenvs.get_secure('DATABASE_URL')
        self.password = simpleenvs.get_secure('DB_PASSWORD')
        
        if self.url:
            print("✅ Database config loaded from parent module")

# services.py (another child module)  
import simpleenvs

class APIClient:
    def __init__(self):
        # Also uses the same SecureEnvLoader automatically
        self.api_key = simpleenvs.get_secure('API_KEY')
        self.secret = simpleenvs.get_secure('API_SECRET')
```

#### Memory Introspection

The discovery mechanism uses Python's garbage collector to safely find existing SecureEnvLoader instances:

```python
def _find_secure_loader_in_memory() -> Optional[SecureEnvLoader]:
    """Find existing SecureEnvLoader instance in memory"""
    try:
        for obj in gc.get_objects():
            if (isinstance(obj, SecureEnvLoader) 
                and hasattr(obj, "_SecureEnvLoader__env_data")
                and obj._SecureEnvLoader__env_data):  # Has loaded data
                return obj
    except Exception:
        pass
    return None
```

#### Security Guarantees

Cross-module access maintains all security properties:

- ✅ **Memory Isolation**: Data still not in `os.environ`
- ✅ **Access Logging**: All access attempts logged
- ✅ **Session Tracking**: Same session ID across modules
- ✅ **Integrity**: File hashes preserved

#### Web Application Pattern

Perfect for web applications with multiple modules:

```python
# app.py - FastAPI application
from fastapi import FastAPI
import simpleenvs

app = FastAPI()

@app.on_event("startup")
async def startup():
    # Load secrets once at startup
    await simpleenvs.load_secure('.env.secrets')

# models/user.py - Database models
import simpleenvs

class UserModel:
    def __init__(self):
        # Automatically uses secrets from app.py
        self.db_url = simpleenvs.get_secure('DATABASE_URL')
        self.jwt_secret = simpleenvs.get_secure('JWT_SECRET')

# services/email.py - Email service
import simpleenvs

class EmailService:
    def __init__(self):
        # Also uses secrets from app.py
        self.smtp_password = simpleenvs.get_secure('SMTP_PASSWORD')
        self.api_key = simpleenvs.get_secure('EMAIL_API_KEY')

# routes/auth.py - Authentication routes
import simpleenvs

def verify_token(token):
    # JWT secret available here too
    secret = simpleenvs.get_secure('JWT_SECRET')
    return jwt.decode(token, secret, algorithms=['HS256'])
```

#### Multiple Loader Discovery

If multiple SecureEnvLoaders exist, the system finds the first one with loaded data:

```python
# Check all loaders in memory
loaders = simpleenvs.get_all_secure_loaders()
print(f"Found {len(loaders)} SecureEnvLoader instances")

# Get security info from active loader
if simpleenvs.is_loaded_secure():
    info = simpleenvs.get_security_info()
    print(f"Active session: {info['session_id']}")
```

#### Best Practices

1. **Load Once**: Load secrets in main module during startup
2. **Check Availability**: Verify loader exists before accessing
3. **Consistent Access**: Use same getter functions across modules

```python
# Defensive programming
def get_database_config():
    if not simpleenvs.is_loaded_secure():
        raise RuntimeError("Secure environment not loaded")
    
    return {
        'url': simpleenvs.get_secure('DATABASE_URL'),
        'password': simpleenvs.get_secure('DB_PASSWORD')
    }
```

### Custom Security Hooks

```python
class CustomSecureLoader(SecureEnvLoader):
    def __init__(self, security_callback=None):
        super().__init__()
        self.security_callback = security_callback
    
    def __log_access(self, operation, key=None, success=True):
        super()._SecureEnvLoader__log_access(operation, key, success)
        
        # Custom security monitoring
        if self.security_callback and not success:
            self.security_callback(operation, key, success)

# Usage
def security_alert(operation, key, success):
    print(f"🚨 Security event: {operation} failed for key {key}")

loader = CustomSecureLoader(security_callback=security_alert)
```

### Integration with Security Tools

```python
# Integration with security monitoring systems
import logging

# Configure security logger
security_logger = logging.getLogger('simpleenvs.security')
security_logger.setLevel(logging.WARNING)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
))
security_logger.addHandler(handler)

# Log security events
def log_security_event(event_type, details):
    security_logger.warning(f"{event_type}: {details}")
```

---

## Need Help?

**Security Questions:**
- 🐛 [Report security issues](https://github.com/vmintf/SimpleEnvs-Python/security)
- 📧 [Contact security team](mailto:vmintf@gmail.com)
- 💬 [Security discussions](https://github.com/vmintf/SimpleEnvs-Python/discussions)

**Resources:**
- 📚 [API Reference](api-reference.md)
- 🚀 [Quick Start](quickstart.md)

---

**Remember:** Security is a process, not a product. Regularly review and update your security practices! 🔒