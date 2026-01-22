#!/usr/bin/env python3
"""
Run tests and display results
"""
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/test_app.py", "-v", "--tb=short"],
    cwd="/workspaces/skills-getting-started-with-github-copilot",
    capture_output=False
)
sys.exit(result.returncode)
