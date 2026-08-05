#!/usr/bin/env python3
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

    # Platform-correct separator for PyInstaller --add-data (':' on POSIX, ';' on Windows)
    add_data = None
    resources_dir = "resources"
    if os.path.isdir(resources_dir):
        add_data = f"{resources_dir}{os.pathsep}{resources_dir}"
    else:
        print(f"Warning: resources directory '{resources_dir}' not found — skipping --add-data")

    # Icon (optional)
    icon_path = os.path.join(resources_dir, "icon.ico")
    icon_flag = None
    if os.path.isfile(icon_path):
        icon_flag = f"--icon={icon_path}"
    else:
        print(f"Warning: icon file '{icon_path}' not found — will build without custom icon")

    # Build command pieces
    cmd = [sys.executable, "-m", "PyInstaller", "--onefile", "--windowed", "--name=TradingSignalSystem"]

    if icon_flag:
        cmd.append(icon_flag)

    if add_data:
        cmd.append(f"--add-data={add_data}")

    hidden_imports = [
        "PyQt6",
        "PyQt6.QtWidgets",
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "sqlalchemy",
        "sqlalchemy.sql.default_comparator",
        "pandas",
        "numpy",
        "ccxt",
        "yfinance",
        "telegram",
        "apscheduler",
        "matplotlib",
        "pyqtgraph",
    ]
    for hi in hidden_imports:
        cmd.append(f"--hidden-import={hi}")

    collect_all = ["telegram", "ccxt"]
    for c in collect_all:
        cmd.append(f"--collect-all={c}")

    cmd.append("main.py")

    print("\nRunning PyInstaller...")
    print(f"Command: {' '.join(cmd)}\n")

    try:
        # Capture output so we print full logs into Actions output
        result = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError as e:
        print("Failed to run PyInstaller: executable not found.")
        print(str(e))
        sys.exit(1)

    # Always print stdout/stderr so CI logs contain the full PyInstaller output
    if result.stdout:
        print("=== PyInstaller stdout ===")
        print(result.stdout)
    if result.stderr:
        print("=== PyInstaller stderr ===")
        print(result.stderr)

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
            sys.exit(1)
    else:
        print(f"\nBuild failed with return code: {result.returncode}")
        # exit with same code so Actions step is marked failed and logs are visible
        sys.exit(result.returncode)


if __name__ == "__main__":
    build()
