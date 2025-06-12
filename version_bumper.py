#!/usr/bin/env python3
"""
Automatic version bumping script for SimpleEnvs
Usage:
    python version_bump.py patch    # 1.0.4 -> 1.0.5
    python version_bump.py minor    # 1.0.4 -> 1.1.0
    python version_bump.py major    # 1.0.4 -> 2.0.0
    python version_bump.py auto     # Auto-detect based on commit messages
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


class VersionBumper:
    def __init__(self):
        self.constants_file = Path("src/simpleenvs/constants.py")
        self.version_pattern = r'VERSION = ["\']([0-9]+\.[0-9]+\.[0-9]+)["\']'

    def get_current_version(self) -> str:
        """Get current version from constants.py"""
        if not self.constants_file.exists():
            raise FileNotFoundError(f"Constants file not found: {self.constants_file}")

        content = self.constants_file.read_text()
        match = re.search(self.version_pattern, content)
        if not match:
            raise ValueError("Version not found in constants.py")

        return match.group(1)

    def parse_version(self, version: str) -> Tuple[int, int, int]:
        """Parse version string into tuple"""
        parts = version.split(".")
        if len(parts) != 3:
            raise ValueError(f"Invalid version format: {version}")

        return tuple(int(part) for part in parts)

    def bump_version(self, current: str, bump_type: str) -> str:
        """Bump version based on type"""
        major, minor, patch = self.parse_version(current)

        if bump_type == "major":
            return f"{major + 1}.0.0"
        elif bump_type == "minor":
            return f"{major}.{minor + 1}.0"
        elif bump_type == "patch":
            return f"{major}.{minor}.{patch + 1}"
        else:
            raise ValueError(f"Invalid bump type: {bump_type}")

    def update_constants_file(self, new_version: str) -> None:
        """Update VERSION in constants.py"""
        content = self.constants_file.read_text()

        # Replace version
        new_content = re.sub(
            self.version_pattern, f'VERSION = "{new_version}"', content
        )

        if new_content == content:
            raise ValueError("Failed to update version in constants.py")

        self.constants_file.write_text(new_content)
        print(f"✅ Updated {self.constants_file} with version {new_version}")

    def get_recent_commits(self, since_tag: str = None) -> List[str]:
        """Get recent commit messages"""
        try:
            if since_tag:
                cmd = [
                    "git",
                    "log",
                    f"{since_tag}..HEAD",
                    "--oneline",
                    "--pretty=format:%s",
                ]
            else:
                cmd = ["git", "log", "-10", "--oneline", "--pretty=format:%s"]

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip().split("\n")
        except Exception:
            pass
        return []

    def auto_detect_bump_type(self) -> str:
        """Auto-detect bump type based on commit messages"""
        commits = self.get_recent_commits()

        # Keywords for different bump types
        major_keywords = ["BREAKING", "breaking change", "major:", "!:"]
        minor_keywords = ["feat:", "feature:", "minor:", "add:", "new:"]
        patch_keywords = [
            "fix:",
            "patch:",
            "docs:",
            "doc:",
            "chore:",
            "style:",
            "refactor:",
            "test:",
        ]

        has_major = any(
            any(keyword in commit.lower() for keyword in major_keywords)
            for commit in commits
        )
        has_minor = any(
            any(keyword in commit.lower() for keyword in minor_keywords)
            for commit in commits
        )
        has_patch = any(
            any(keyword in commit.lower() for keyword in patch_keywords)
            for commit in commits
        )

        if has_major:
            return "major"
        elif has_minor:
            return "minor"
        elif has_patch or commits:  # Default to patch if any commits
            return "patch"
        else:
            return "patch"  # Safe default

    def get_last_git_tag(self) -> str:
        """Get the last git tag"""
        try:
            result = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                return result.stdout.strip().lstrip("v")
        except Exception:
            pass
        return None

    def create_git_tag(self, version: str, push: bool = False) -> None:
        """Create git tag for new version"""
        try:
            tag_name = f"v{version}"

            # Create tag
            subprocess.run(
                ["git", "tag", "-a", tag_name, "-m", f"Release {version}"], check=True
            )
            print(f"✅ Created git tag: {tag_name}")

            if push:
                # Push tag
                subprocess.run(["git", "push", "origin", tag_name], check=True)
                print(f"✅ Pushed tag to origin: {tag_name}")

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create/push git tag: {e}")

    def bump(
        self, bump_type: str, create_tag: bool = False, push_tag: bool = False
    ) -> str:
        """Main bump function"""
        # Get current version
        current_version = self.get_current_version()
        print(f"📦 Current version: {current_version}")

        # Auto-detect if requested
        if bump_type == "auto":
            bump_type = self.auto_detect_bump_type()
            print(f"🤖 Auto-detected bump type: {bump_type}")

        # Calculate new version
        new_version = self.bump_version(current_version, bump_type)
        print(f"🚀 New version: {new_version}")

        # Update files
        self.update_constants_file(new_version)

        # Create git tag if requested
        if create_tag:
            self.create_git_tag(new_version, push=push_tag)

        print(f"✅ Version bumped from {current_version} to {new_version}")
        return new_version


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python version_bump.py [patch|minor|major|auto] [--tag] [--push]")
        print("Examples:")
        print("  python version_bump.py patch          # Bump patch version")
        print("  python version_bump.py minor --tag    # Bump minor and create tag")
        print(
            "  python version_bump.py auto --tag --push  # Auto-detect, tag, and push"
        )
        sys.exit(1)

    bump_type = sys.argv[1]
    create_tag = "--tag" in sys.argv
    push_tag = "--push" in sys.argv

    if bump_type not in ["patch", "minor", "major", "auto"]:
        print(f"❌ Invalid bump type: {bump_type}")
        print("Valid types: patch, minor, major, auto")
        sys.exit(1)

    try:
        bumper = VersionBumper()
        new_version = bumper.bump(bump_type, create_tag, push_tag)

        print(f"\n🎉 Successfully bumped to v{new_version}!")

        if create_tag:
            print("\n📋 Next steps:")
            print(
                "1. Commit the version change: git add . && git commit -m 'Bump version to v{}'".format(
                    new_version
                )
            )
            if not push_tag:
                print("2. Push the tag: git push origin v{}".format(new_version))
            print("3. Create a GitHub release")
        else:
            print("\n📋 Next steps:")
            print(
                "1. Commit the changes: git add . && git commit -m 'Bump version to v{}'".format(
                    new_version
                )
            )
            print(
                "2. Create a tag: python version_bump.py {} --tag --push".format(
                    bump_type
                )
            )

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
