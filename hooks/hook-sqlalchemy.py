# hooks/hook-sqlalchemy.py
# PyInstaller hook to collect SQLAlchemy modules and data files
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

hiddenimports = collect_submodules('sqlalchemy')
hiddenimports += collect_submodules('sqlalchemy.ext')
hiddenimports += collect_submodules('sqlalchemy.orm')

datas = collect_data_files('sqlalchemy')
