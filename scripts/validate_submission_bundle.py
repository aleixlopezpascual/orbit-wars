#!/usr/bin/env python3
"""
validate_submission_bundle.py — Pre-submission sanity gate for Kaggle submission bundles.

Checks that a submission tarball/zip:
  1. Exists and is readable
  2. Contains main.py
  3. main.py can be imported (catches import/syntax errors early)
  4. All declared dependencies (orbit_lite, etc.) are present
  5. Required files are accessible

Usage:
    python3 scripts/validate_submission_bundle.py submission.tar.gz
    python3 scripts/validate_submission_bundle.py submission.zip
    python3 scripts/validate_submission_bundle.py --help

Exit codes:
    0 = PASS (bundle is valid)
    1 = FAIL (validation error; details printed)
"""

import argparse
import importlib.util
import os
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path
from typing import Tuple, Optional


def validate_bundle(bundle_path: str) -> Tuple[bool, str]:
    """
    Validate a submission bundle. Returns (success, message).
    """
    bundle_path = Path(bundle_path).resolve()
    
    # Check existence
    if not bundle_path.exists():
        return False, f"Bundle not found: {bundle_path}"
    
    if not bundle_path.is_file():
        return False, f"Not a file: {bundle_path}"
    
    # Determine archive type
    if bundle_path.suffix == ".gz" or str(bundle_path).endswith(".tar.gz"):
        archive_type = "tar"
    elif bundle_path.suffix == ".zip":
        archive_type = "zip"
    else:
        return False, f"Unknown archive type (not .tar.gz or .zip): {bundle_path}"
    
    try:
        # Extract to temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            try:
                if archive_type == "tar":
                    with tarfile.open(bundle_path, "r:gz") as tar:
                        tar.extractall(tmpdir)
                else:
                    with zipfile.ZipFile(bundle_path, "r") as zf:
                        zf.extractall(tmpdir)
            except Exception as e:
                return False, f"Failed to extract archive: {e}"
            
            # Check for main.py
            main_py = tmpdir / "main.py"
            if not main_py.exists():
                # Search for main.py in subdirectories
                main_py_list = list(tmpdir.rglob("main.py"))
                if not main_py_list:
                    return False, "main.py not found in bundle"
                main_py = main_py_list[0]
            
            # Check for known dependencies
            missing_deps = []
            for dep in ["orbit_lite", "orbit_lite/"]:
                dep_path = tmpdir / dep
                if not dep_path.exists():
                    # Try with trailing slash for directories
                    dep_path = tmpdir / (dep.rstrip("/"))
                    if not dep_path.exists() and dep.endswith("/"):
                        missing_deps.append(dep.rstrip("/"))
            
            if missing_deps:
                return False, f"Missing dependencies: {missing_deps}"
            
            # Try to import main.py
            try:
                spec = importlib.util.spec_from_file_location("_main_submit", main_py)
                if spec is None or spec.loader is None:
                    return False, f"Could not load spec for {main_py}"
                
                mod = importlib.util.module_from_spec(spec)
                
                # Add tmpdir to sys.path so relative imports work
                sys.path.insert(0, str(tmpdir))
                try:
                    sys.modules["_main_submit"] = mod
                    spec.loader.exec_module(mod)
                finally:
                    sys.path.remove(str(tmpdir))
                    sys.modules.pop("_main_submit", None)
                
                # Check for agent() function
                if not hasattr(mod, "agent"):
                    return False, "main.py does not export an agent() function"
                
                if not callable(mod.agent):
                    return False, "agent in main.py is not callable"
            
            except SyntaxError as e:
                return False, f"Syntax error in main.py: {e}"
            except ImportError as e:
                return False, f"Import error in main.py: {e}"
            except Exception as e:
                return False, f"Error loading main.py: {e}"
            
            return True, f"✅ Bundle validated: {bundle_path.name}"
    
    except Exception as e:
        return False, f"Unexpected error during validation: {e}"


def main():
    parser = argparse.ArgumentParser(
        description="Validate a Kaggle submission bundle before upload.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "bundle",
        help="Path to submission bundle (.tar.gz or .zip)"
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true",
        help="Suppress output (exit code only)"
    )
    
    args = parser.parse_args()
    
    success, message = validate_bundle(args.bundle)
    
    if not args.quiet:
        print(message)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
