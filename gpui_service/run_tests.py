#!/usr/bin/env python3
"""
Test runner script for gpui_service.
Ensures Python 3.9+ compatibility and runs tests.
"""
import sys
import subprocess
import os

def check_python_version():
    """Check if Python version is at least 3.9."""
    if sys.version_info < (3, 9):
        print(f"ERROR: Python 3.9+ required, but running {sys.version}")
        print("Use 'python3' instead of 'python' if available.")
        return False
    return True

def run_tests():
    """Run tests using unittest discovery."""
    if not check_python_version():
        sys.exit(1)

    print(f"Python {sys.version}")
    print("Running tests...")

    # Run unittest discovery
    result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-v"],
                           cwd=os.path.dirname(__file__))
    return result.returncode

def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--pytest":
        # Try to run pytest
        try:
            import pytest
            sys.exit(pytest.main(["-v"]))
        except ImportError:
            print("pytest not installed, falling back to unittest")
            sys.exit(run_tests())
    else:
        sys.exit(run_tests())

if __name__ == "__main__":
    main()