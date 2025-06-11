# docs/build.py
"""
Cross-platform documentation build script
Usage: python build.py [command]
Commands: html, clean, serve, help
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(cmd):
    """Run command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {e}")
        return False


def get_version():
    """Get SimpleEnvs version dynamically"""
    try:
        # Try to import from installed package
        import simpleenvs

        return simpleenvs.__version__
    except ImportError:
        # Try to read from constants.py
        try:
            import sys
            from pathlib import Path

            # Add src directory to path
            src_path = Path(__file__).parent.parent / "src"
            if src_path.exists():
                sys.path.insert(0, str(src_path))

            from simpleenvs.constants import VERSION

            return VERSION
        except ImportError:
            return "unknown"


def build_html():
    """Build HTML documentation"""
    version = get_version()
    print(f"🔨 Building HTML documentation for SimpleEnvs v{version}...")
    success = run_command("sphinx-build -b html . _build/html")
    if success:
        print("✅ Build successful!")
        print("📄 Open _build/html/index.html to view documentation")
        print(f"📦 Documentation built for version: {version}")
    else:
        print("❌ Build failed!")
    return success


def clean_build():
    """Clean build directory"""
    print("🧹 Cleaning build directory...")
    build_dir = Path("_build")
    if build_dir.exists():
        shutil.rmtree(build_dir)
        print("✅ Build directory cleaned!")
    else:
        print("ℹ️ Build directory doesn't exist")


def serve_docs():
    """Start development server"""
    print("🚀 Starting development server...")
    print("📱 Documentation will be available at http://localhost:8000")
    print("🔄 Auto-reload enabled - changes will be reflected automatically")
    print("🛑 Press Ctrl+C to stop")

    try:
        run_command("sphinx-autobuild . _build/html --host 127.0.0.1 --port 8000")
    except KeyboardInterrupt:
        print("\n👋 Server stopped!")


def show_help():
    """Show help message"""
    print(
        """
📚 SimpleEnvs Documentation Builder

Usage: python build.py [command]

Available commands:
  html     Build HTML documentation
  clean    Clean build directory  
  serve    Start development server with auto-reload
  help     Show this help message

Examples:
  python build.py html     # Build docs
  python build.py serve    # Start dev server
  python build.py clean    # Clean and rebuild

🔧 Requirements:
  pip install -r requirements.txt
    """
    )


def main():
    """Main entry point"""
    # Change to docs directory if not already there
    if not Path("conf.py").exists():
        docs_dir = Path(__file__).parent
        if docs_dir.name == "docs":
            os.chdir(docs_dir)
        else:
            print("❌ Please run this script from the docs directory")
            sys.exit(1)

    # Get command from args
    command = sys.argv[1] if len(sys.argv) > 1 else "help"

    # Execute command
    if command == "html":
        success = build_html()
        sys.exit(0 if success else 1)
    elif command == "clean":
        clean_build()
    elif command == "serve":
        serve_docs()
    elif command == "help":
        show_help()
    else:
        print(f"❌ Unknown command: {command}")
        show_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
