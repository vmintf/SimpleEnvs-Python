# 📦 SimpleEnvs Version Management Guide

## 🚀 Quick Version Bumping

### Manual Bumping (Local)
```bash
# Patch version (1.0.4 → 1.0.5) - Bug fixes, docs
python version_bump.py patch

# Minor version (1.0.4 → 1.1.0) - New features
python version_bump.py minor

# Major version (1.0.4 → 2.0.0) - Breaking changes
python version_bump.py major

# Auto-detect based on commit messages
python version_bump.py auto
```

### With Git Tags
```bash
# Bump and create git tag
python version_bump.py patch --tag

# Bump, create tag, and push to origin
python version_bump.py patch --tag --push
```

## 🤖 Automated Version Bumping

### 1. Automatic on Docs Changes
When you push commits with `docs:` prefix to main branch:
```bash
git commit -m "docs: update installation guide"
git push origin main
# → Automatically bumps patch version (1.0.4 → 1.0.5)
```

### 2. Manual Trigger (GitHub Actions)
1. Go to `Actions` tab
2. Select `Auto Version Bump` workflow  
3. Click `Run workflow`
4. Choose bump type and options

### 3. Smart Weekly Release
Every Monday at 9 AM, checks for unreleased changes and auto-releases if found.

## 📋 Commit Message Conventions

Our auto-detection uses these keywords:

### 🔴 Major Version (Breaking Changes)
```bash
git commit -m "BREAKING: remove deprecated API"
git commit -m "major: complete API redesign"
git commit -m "feat!: new authentication system"
```

### 🟡 Minor Version (New Features)
```bash
git commit -m "feat: add async loading support"
git commit -m "feature: new security mode"
git commit -m "minor: improve performance"
```

### 🟢 Patch Version (Bug Fixes, Docs)
```bash
git commit -m "fix: handle empty .env files"
git commit -m "docs: update API reference"
git commit -m "chore: update dependencies"
git commit -m "style: improve code formatting"
git commit -m "test: add coverage for edge cases"
```

## 🎯 Version Strategy

**SimpleEnvs follows Semantic Versioning (SemVer):**

- **Patch (x.y.Z)**: Bug fixes, documentation, small improvements
- **Minor (x.Y.0)**: New features, backward-compatible changes
- **Major (X.0.0)**: Breaking changes, API redesign

### When to Use Each:

| Change Type | Example | Version Bump |
|-------------|---------|--------------|
| Fix typo in docs | `docs: fix typo in README` | Patch |
| Add new getter function | `feat: add get_float_secure()` | Minor |
| Remove deprecated API | `BREAKING: remove old load_env()` | Major |
| Security patch | `fix: validate file paths` | Patch |
| New security mode | `feat: add enterprise mode` | Minor |

## 🔄 Release Workflow

### For Documentation Changes:
```bash
# 1. Make your changes
vim docs/installation.md

# 2. Commit with docs: prefix
git commit -m "docs: improve installation instructions"

# 3. Push to main
git push origin main

# 4. GitHub Actions automatically:
#    - Bumps patch version (1.0.4 → 1.0.5)
#    - Commits version change
#    - Updates documentation site
```

### For Feature/Bug Fix:
```bash
# 1. Create feature branch
git checkout -b feature/new-loader

# 2. Make changes and commit
git commit -m "feat: add custom loader support"

# 3. Push and create PR
git push origin feature/new-loader

# 4. After PR merge, manually trigger release:
#    Actions → Auto Version Bump → Run workflow → Minor
```

### For Emergency Release:
```bash
# Quick patch release
python version_bump.py patch --tag --push

# Then trigger PyPI deployment
# Actions → Deploy to PyPI → Run workflow → pypi
```

## 📊 Version History Tracking

### Check Current Version:
```bash
# From code
python -c "import simpleenvs; print(simpleenvs.__version__)"

# From constants file
grep VERSION src/simpleenvs/constants.py

# From git tags
git tag --sort=-version:refname | head -5
```

### Version Changelog:
```bash
# Changes since last release
git log $(git describe --tags --abbrev=0)..HEAD --oneline

# Compare two versions
git log v1.0.3..v1.0.4 --oneline
```

## 🔧 Configuration

### GitHub Repository Settings:
1. **Actions permissions**: Read and write
2. **Branch protection**: Require PR for main branch
3. **Secrets**: Add PyPI tokens for deployment

### Environment Variables:
- `GITHUB_TOKEN`: Automatic (for creating releases)
- `PYPI_API_TOKEN`: Manual (for PyPI deployment)

## 🎉 Best Practices

### ✅ Do:
- Use conventional commit messages
- Test locally before releasing
- Document breaking changes
- Keep patch releases small and focused

### ❌ Don't:
- Skip version numbers
- Release untested code
- Make breaking changes in patch releases
- Forget to update documentation

## 🆘 Troubleshooting

### Version Bump Failed:
```bash
# Check if constants.py exists
ls -la src/simpleenvs/constants.py

# Verify file format
grep -n VERSION src/simpleenvs/constants.py
```

### Git Tag Issues:
```bash
# Delete local tag
git tag -d v1.0.5

# Delete remote tag  
git push origin --delete v1.0.5

# Re-create tag
python version_bump.py patch --tag --push
```

### PyPI Deployment Failed:
1. Check if version already exists on PyPI
2. Verify API token in GitHub secrets
3. Ensure package builds successfully locally

---

**Happy versioning!** 🎉 Keep those releases coming! 🚀