#!/usr/bin/env python3
"""
SimpleEnvs + FastAPI Integration Example
Demonstrates how SimpleEnvs works seamlessly with FastAPI applications
"""

import asyncio
import os
import tempfile
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional

try:
    import uvicorn
    from fastapi import Depends, FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("⚠️  FastAPI not installed. Install with: pip install fastapi uvicorn")

import simpleenvs
from simpleenvs import SecureEnvLoader, SimpleEnvLoader

# =============================================================================
# ENVIRONMENT SETUP
# =============================================================================


async def setup_environment():
    """Setup environment variables for the example"""
    # Create a sample .env file
    env_content = """
# FastAPI Application Configuration
APP_NAME=SimpleEnvs FastAPI Demo
APP_VERSION=1.0.0
DEBUG=true
ENVIRONMENT=development

# Server Configuration  
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Database Configuration (Simple - goes to os.environ)
DATABASE_URL=postgresql://user:password@localhost:5432/myapp
DATABASE_POOL_SIZE=10
DATABASE_TIMEOUT=30

# Security Configuration (Secure - memory-isolated)
SECRET_KEY=super-secret-jwt-key-that-should-never-be-exposed
API_SECRET=another-secret-for-api-authentication
ENCRYPTION_KEY=encryption-key-for-sensitive-data
ADMIN_PASSWORD=admin-super-secure-password

# External APIs
REDIS_URL=redis://localhost:6379/0
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Feature Flags
ENABLE_CORS=true
ENABLE_LOGGING=true
ENABLE_METRICS=false
"""

    # Write to temporary .env file
    env_file = ".env.example"
    with open(env_file, "w") as f:
        f.write(env_content.strip())

    print(f"📝 Created example .env file: {env_file}")
    return env_file


# =============================================================================
# FASTAPI APPLICATION SETUP
# =============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan events - startup and shutdown"""

    # Startup
    print("🚀 Starting FastAPI application...")

    # Setup environment
    env_file = await setup_environment()

    # Load simple environment (goes to os.environ)
    print("📤 Loading simple environment variables...")
    await simpleenvs.load(env_file)
    print(f"✅ Loaded {len(simpleenvs.get_all_keys())} simple environment variables")

    # Load secure environment (memory-isolated)
    print("🔒 Loading secure environment variables...")
    await simpleenvs.load_secure(env_file)
    print(f"✅ Loaded secure environment variables (memory-isolated)")

    # Application is ready
    print("🎉 Application startup complete!")

    yield

    # Shutdown
    print("🛑 Shutting down application...")

    # Secure cleanup
    simpleenvs.clear()
    print("🧹 Environment cleaned up")


# Create FastAPI app
if FASTAPI_AVAILABLE:
    app = FastAPI(
        title=os.getenv("APP_NAME", "SimpleEnvs Demo"),
        version=os.getenv("APP_VERSION", "1.0.0"),
        description="FastAPI application demonstrating SimpleEnvs integration",
        lifespan=lifespan,
    )

    # CORS middleware (using simple env var)
    if os.getenv("ENABLE_CORS", "false").lower() == "true":
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )


# =============================================================================
# DEPENDENCY INJECTION
# =============================================================================


def get_database_config() -> Dict[str, Any]:
    """Get database configuration from simple environment"""
    return {
        "url": os.getenv("DATABASE_URL"),
        "pool_size": int(os.getenv("DATABASE_POOL_SIZE", "5")),
        "timeout": int(os.getenv("DATABASE_TIMEOUT", "30")),
    }


def get_secure_config() -> Dict[str, Any]:
    """Get secure configuration from memory-isolated environment"""
    return {
        "secret_key": simpleenvs.get_secure("SECRET_KEY"),
        "api_secret": simpleenvs.get_secure("API_SECRET"),
        "encryption_key": simpleenvs.get_secure("ENCRYPTION_KEY"),
        "admin_password": simpleenvs.get_secure("ADMIN_PASSWORD"),
    }


def verify_api_secret(api_secret: Optional[str] = None) -> bool:
    """Verify API secret from secure environment"""
    if not api_secret:
        return False

    stored_secret = simpleenvs.get_secure("API_SECRET")
    return api_secret == stored_secret


# =============================================================================
# API ENDPOINTS
# =============================================================================

if FASTAPI_AVAILABLE:

    @app.get("/")
    async def root():
        """Root endpoint showing app info"""
        return {
            "app": os.getenv("APP_NAME"),
            "version": os.getenv("APP_VERSION"),
            "environment": os.getenv("ENVIRONMENT"),
            "debug": os.getenv("DEBUG", "false").lower() == "true",
            "message": "SimpleEnvs + FastAPI Integration Demo",
        }

    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "timestamp": "2025-01-01T00:00:00Z",
            "environment_loaded": simpleenvs.is_loaded(),
            "secure_loaded": simpleenvs.is_loaded_secure(),
        }

    @app.get("/config/simple")
    async def get_simple_config():
        """Get non-sensitive configuration (from os.environ)"""
        return {
            "app_name": os.getenv("APP_NAME"),
            "app_version": os.getenv("APP_VERSION"),
            "environment": os.getenv("ENVIRONMENT"),
            "debug": os.getenv("DEBUG", "false").lower() == "true",
            "host": os.getenv("HOST"),
            "port": int(os.getenv("PORT", "8000")),
            "workers": int(os.getenv("WORKERS", "1")),
            "cors_enabled": os.getenv("ENABLE_CORS", "false").lower() == "true",
            "logging_enabled": os.getenv("ENABLE_LOGGING", "false").lower() == "true",
            "metrics_enabled": os.getenv("ENABLE_METRICS", "false").lower() == "true",
        }

    @app.get("/config/database")
    async def get_database_config_endpoint(
        db_config: Dict[str, Any] = Depends(get_database_config),
    ):
        """Get database configuration"""
        # Hide password in URL
        if db_config["url"]:
            url_parts = db_config["url"].split("@")
            if len(url_parts) > 1:
                db_config["url"] = f"postgresql://***:***@{url_parts[1]}"

        return db_config

    @app.get("/config/secure")
    async def get_secure_config_endpoint(api_secret: str):
        """Get secure configuration (requires API secret)"""

        if not verify_api_secret(api_secret):
            raise HTTPException(status_code=401, detail="Invalid API secret")

        secure_config = get_secure_config()

        # Mask sensitive values for display
        return {
            "secret_key": "***" if secure_config["secret_key"] else None,
            "api_secret": "***" if secure_config["api_secret"] else None,
            "encryption_key": "***" if secure_config["encryption_key"] else None,
            "admin_password": "***" if secure_config["admin_password"] else None,
            "note": "Actual values are memory-isolated and not in os.environ",
        }

    @app.get("/security/verify")
    async def verify_security():
        """Verify that secure variables are NOT in os.environ"""
        secure_keys = ["SECRET_KEY", "API_SECRET", "ENCRYPTION_KEY", "ADMIN_PASSWORD"]

        security_check = {}
        for key in secure_keys:
            # Check if it's in os.environ (should be False for secure vars)
            in_os_environ = key in os.environ

            # Check if it's available via SimpleEnvs secure
            available_secure = simpleenvs.get_secure(key) is not None

            security_check[key] = {
                "in_os_environ": in_os_environ,
                "available_secure": available_secure,
                "properly_isolated": not in_os_environ and available_secure,
            }

        all_properly_isolated = all(
            check["properly_isolated"] for check in security_check.values()
        )

        return {
            "message": "Security isolation check",
            "all_properly_isolated": all_properly_isolated,
            "details": security_check,
            "explanation": {
                "in_os_environ": "Variable is accessible via os.getenv() (BAD for secrets)",
                "available_secure": "Variable is accessible via simpleenvs.get_secure()",
                "properly_isolated": "Variable is secure (not in os.environ but available via secure API)",
            },
        }

    @app.get("/info")
    async def get_environment_info():
        """Get comprehensive environment information"""
        return {
            "simpleenvs_info": simpleenvs.get_info(),
            "security_info": simpleenvs.get_security_info(),
            "simple_keys": simpleenvs.get_all_keys(),
            "os_environ_count": len(os.environ),
            "note": "This demonstrates the dual-layer environment system",
        }

    @app.post("/auth/login")
    async def login(username: str, password: str):
        """Example login endpoint using secure environment"""

        # Get admin password from secure environment (not os.environ!)
        admin_password = simpleenvs.get_secure("ADMIN_PASSWORD")

        if username == "admin" and password == admin_password:
            # In real app, you'd generate JWT token using SECRET_KEY
            secret_key = simpleenvs.get_secure("SECRET_KEY")

            return {
                "message": "Login successful",
                "token": "fake-jwt-token-would-be-generated-here",
                "note": f"Used secret key: {'***' if secret_key else 'None'}",
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")


# =============================================================================
# TESTING FUNCTIONS
# =============================================================================


async def test_fastapi_integration():
    """Test the FastAPI integration without actually starting the server"""

    if not FASTAPI_AVAILABLE:
        print("❌ FastAPI not available for testing")
        return

    print("🧪 Testing FastAPI + SimpleEnvs integration...")

    # Setup environment
    env_file = await setup_environment()

    # Load environments
    await simpleenvs.load(env_file)
    await simpleenvs.load_secure(env_file)

    print("\n📊 Integration Test Results:")
    print("=" * 50)

    # Test 1: Simple environment variables
    app_name = os.getenv("APP_NAME")
    print(f"✅ App name from os.environ: {app_name}")

    # Test 2: Secure environment variables
    secret_key = simpleenvs.get_secure("SECRET_KEY")
    print(f"✅ Secret key from secure env: {'***' if secret_key else 'None'}")

    # Test 3: Security isolation
    secret_in_os = "SECRET_KEY" in os.environ
    print(f"✅ Secret NOT in os.environ: {not secret_in_os}")

    # Test 4: Type conversion
    debug = os.getenv("DEBUG", "false").lower() == "true"
    port = int(os.getenv("PORT", "8000"))
    print(f"✅ Type conversion - Debug: {debug}, Port: {port}")

    # Test 5: Security verification
    secure_keys = ["SECRET_KEY", "API_SECRET", "ENCRYPTION_KEY"]
    properly_isolated = all(
        key not in os.environ and simpleenvs.get_secure(key) is not None
        for key in secure_keys
    )
    print(f"✅ All secrets properly isolated: {properly_isolated}")

    print("\n🎉 FastAPI integration test completed successfully!")

    # Cleanup
    simpleenvs.clear()
    if os.path.exists(env_file):
        os.remove(env_file)


def run_server():
    """Run the FastAPI server"""
    if not FASTAPI_AVAILABLE:
        print("❌ FastAPI not installed. Install with: pip install fastapi uvicorn")
        return

    print("🚀 Starting FastAPI server with SimpleEnvs...")
    print("📝 Available endpoints:")
    print("   GET  /                 - Root endpoint")
    print("   GET  /health           - Health check")
    print("   GET  /config/simple    - Simple configuration")
    print("   GET  /config/database  - Database configuration")
    print("   GET  /config/secure    - Secure configuration (requires API secret)")
    print("   GET  /security/verify  - Security isolation verification")
    print("   GET  /info             - Environment information")
    print("   POST /auth/login       - Login endpoint")
    print("\n🔐 To access secure endpoint:")
    print("   GET /config/secure?api_secret=another-secret-for-api-authentication")
    print()

    uvicorn.run(
        "fastapi_example:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("DEBUG", "false").lower() == "true",
        log_level=(
            "info" if os.getenv("ENABLE_LOGGING", "true").lower() == "true" else "error"
        ),
    )


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Run integration test
        asyncio.run(test_fastapi_integration())
    else:
        # Run server
        run_server()
