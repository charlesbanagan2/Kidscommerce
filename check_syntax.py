#!/usr/bin/env python
"""Verify Python syntax without executing"""
import sys
import py_compile

try:
    py_compile.compile(r'c:\Users\mnban\OneDrive\Desktop\kids\backend\app.py', doraise=True)
    print("✓ app.py has valid Python syntax")
    sys.exit(0)
except py_compile.PyCompileError as e:
    print(f"✗ Syntax error in app.py: {e}")
    sys.exit(1)
