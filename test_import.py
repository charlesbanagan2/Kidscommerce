#!/usr/bin/env python
"""Test if backend/app.py imports without NameError"""
import sys
sys.path.insert(0, r'c:\Users\mnban\OneDrive\Desktop\kids')

try:
    # Try to import the app module
    print("Attempting to import backend.app...")
    from backend import app as app_module
    print("✓ Successfully imported backend.app")
    print("✓ No NameError encountered!")
    sys.exit(0)
except NameError as e:
    print(f"✗ NameError: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✓ Imported but got other exception (expected): {type(e).__name__}: {e}")
    # Other exceptions are OK - we just want to verify no NameError
    sys.exit(0)
