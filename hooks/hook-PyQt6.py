# hooks/hook-PyQt6.py
# PyInstaller hook for PyQt6 to ensure Qt plugins and sip are included.
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

hiddenimports = collect_submodules('PyQt6')
datas = collect_data_files('PyQt6')
