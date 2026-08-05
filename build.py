#!/usr/bin/env python3
"""Build script for creating executable with PyInstaller.

Includes hooks dir and collects sqlalchemy/pandas/PyQt6 resources.
"""
import os
import sys
import subprocess
import shutil

def build():
    print("=" * 60)
    print("Building Trading Signal System...")
    print("=" * 60)

    for dir_name in ["build", "dist"]:
        if os.path.exists(dir_name):
            print(f"Cleaning {dir_name}...")
            shutil.rmtree(dir_name)

    resources_dir = "resources"
    add_data = None
    if os.path.isdir(resources_dir):
        add_data = f"{resources_dir}{os.pathsep}{resources_dir}"
    else:
        print(f"Warning: resources directory '{resources_dir}' not found — skipping --add-data")

    icon_path = os.path.join(resources_dir, "icon.ico")
    icon_flag = None
    if os.path.isfile(icon_path):
        icon_flag = f"--icon={icon_path}"
    else:
        print(f"Warning: icon file '{icon_path}' not found — will build without custom icon")

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
        "PyQt6.sip",
        "sqlalchemy",
        "sqlalchemy.orm",
        "sqlalchemy.ext.declarative",
        "sqlalchemy.sql",
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

    collect_all = ["telegram", "ccxt", "PyQt6", "sqlalchemy", "pandas"]
    for c in collect_all:
        cmd.append(f"--collect-all={c}")

    cmd.append("--additional-hooks-dir=hooks")
    cmd.append("main.py")

    print("\nRunning PyInstaller...")
    print(f"Command: {' '.join(cmd)}\n")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError as e:
        print("Failed to run PyInstaller: executable not found.")
        print(str(e))
        sys.exit(1)

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
            print("BUILD SUCCESSFUL!")
            print(f"Executable: {exe_path}")
            print(f"Size: {size_mb:.1f} MB")
            print("=" * 60)
        else:
            print("\nBuild completed but executable not found.")
            sys.exit(1)
    else:
        print(f"\nBuild failed with return code: {result.returncode}")
        sys.exit(result.returncode)

if __name__ == "__main__":
    build()
