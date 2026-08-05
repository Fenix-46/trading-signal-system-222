"""Build script for creating executable with PyInstaller."""

import os
import sys
import subprocess
import shutil


def build():
    """Build the application into a single executable."""
    print("=" * 60)
    print("Building Trading Signal System...")
    print("=" * 60)

    # Clean previous builds
    for dir_name in ["build", "dist"]:
        if os.path.exists(dir_name):
            print(f"Cleaning {dir_name}...")
            shutil.rmtree(dir_name)

    # Build command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name=TradingSignalSystem",
        "--icon=resources/icon.ico",
        "--add-data=resources;resources",
        "--hidden-import=PyQt6",
        "--hidden-import=PyQt6.QtWidgets",
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtGui",
        "--hidden-import=sqlalchemy",
        "--hidden-import=sqlalchemy.sql.default_comparator",
        "--hidden-import=pandas",
        "--hidden-import=numpy",
        "--hidden-import=ccxt",
        "--hidden-import=yfinance",
        "--hidden-import=telegram",
        "--hidden-import=apscheduler",
        "--hidden-import=matplotlib",
        "--hidden-import=pyqtgraph",
        "--collect-all=telegram",
        "--collect-all=ccxt",
        "main.py"
    ]

    print("\nRunning PyInstaller...")
    print(f"Command: {' '.join(cmd)}\n")

    result = subprocess.run(cmd, capture_output=False)

    if result.returncode == 0:
        exe_path = os.path.join("dist", "TradingSignalSystem.exe")
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print("\n" + "=" * 60)
            print(f"BUILD SUCCESSFUL!")
            print(f"Executable: {exe_path}")
            print(f"Size: {size_mb:.1f} MB")
            print("=" * 60)
        else:
            print("\nBuild completed but executable not found.")
    else:
        print(f"\nBuild failed with return code: {result.returncode}")
        sys.exit(1)


if __name__ == "__main__":
    build()
