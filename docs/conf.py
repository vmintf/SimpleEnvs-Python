# docs/conf.py
"""
Configuration file for Sphinx documentation builder.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(".."))

# Project information
project = "SimpleEnvs"
copyright = "2025, vmintf"
author = "vmintf"

# Get version dynamically
try:
    from version_utils import get_version

    release = get_version()
    version = ".".join(release.split(".")[:2])  # e.g., "1.0.4" -> "1.0"
except ImportError:
    # Simple fallback if version_utils not available
    try:
        import simpleenvs

        release = simpleenvs.__version__
        version = ".".join(release.split(".")[:2])
    except ImportError:
        release = "1.1.3"
        version = "1.1"
        print(f"Warning: Using fallback version: {release}")

print(f"📚 Building documentation for SimpleEnvs v{release}")

# General configuration
extensions = [
    "sphinx.ext.autodoc",  # Auto-generate docs from docstrings
    "sphinx.ext.viewcode",  # Add source code links
    "sphinx.ext.napoleon",  # Google/NumPy style docstrings
    "sphinx.ext.intersphinx",  # Link to other project docs
    "sphinx.ext.todo",  # Todo notes
    "sphinx.ext.coverage",  # Coverage checker
    "myst_parser",  # Markdown support
]

# MyST (Markdown) configuration
myst_enable_extensions = [
    "colon_fence",  # ::: fences
    "deflist",  # Definition lists
    "tasklist",  # Task lists
    "substitution",  # Variable substitution
]

# Source file suffixes
source_suffix = {
    ".rst": None,
    ".md": None,
}

# The master toctree document
master_doc = "index"

# Language settings
language = "en"

# Exclude patterns
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# HTML output options
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "logo_only": False,
    "display_version": True,
    "prev_next_buttons_location": "bottom",
    "style_external_links": False,
    "vcs_pageview_mode": "",
    "style_nav_header_background": "#2980B9",
    # Toc options
    "collapse_navigation": True,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
    "titles_only": False,
}

# Static files
html_static_path = ["_static"]

# Custom CSS
html_css_files = [
    "custom.css",
]

# HTML context
html_context = {
    "display_github": True,
    "github_user": "vmintf",
    "github_repo": "SimpleEnvs-Python",
    "github_version": "main",
    "conf_py_path": "/docs/",
}

# Autodoc settings
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
}

# Napoleon settings (for Google/NumPy style docstrings)
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "aiofiles": ("https://aiofiles.readthedocs.io/en/latest/", None),
}

# Todo extension
todo_include_todos = False
