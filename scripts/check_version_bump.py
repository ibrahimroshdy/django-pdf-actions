#!/usr/bin/env python3
import subprocess
import tomli
import sys
from pathlib import Path

def get_gitversion():
    try:
        # Run GitVersion
        result = subprocess.run(
            ['gitversion', '/config', '.github/GitVersion.yml'],
            capture_output=True,
            text=True,
            check=True
        )
        # Parse the output to get the SemVer
        for line in result.stdout.split('\n'):
            if line.startswith('SemVer:'):
                return line.split(':')[1].strip()
        return None
    except subprocess.CalledProcessError:
        print("Error: GitVersion not found or failed to run.")
        print("Please ensure GitVersion is installed: 'dotnet tool install --global GitVersion.Tool'")
        sys.exit(1)

def get_version_from_pyproject():
    try:
        with open('pyproject.toml', 'rb') as f:
            data = tomli.loads(f.read().decode('utf-8'))
            return data['tool']['poetry']['version']
    except (FileNotFoundError, KeyError, tomli.TOMLDecodeError) as e:
        print(f"Error reading pyproject.toml: {e}")
        sys.exit(1)

def main():
    # Get version from GitVersion
    gitversion = get_gitversion()
    if not gitversion:
        print("Error: Could not determine version from GitVersion")
        sys.exit(1)
    
    # Get version from pyproject.toml
    pyproject_version = get_version_from_pyproject()
    
    # Compare versions
    if gitversion != pyproject_version:
        print(f"Error: Version mismatch")
        print(f"pyproject.toml version: {pyproject_version}")
        print(f"GitVersion version: {gitversion}")
        print("Please update pyproject.toml version to match GitVersion")
        sys.exit(1)
    
    print(f"Version check passed: {gitversion}")
    sys.exit(0)

if __name__ == '__main__':
    main() 