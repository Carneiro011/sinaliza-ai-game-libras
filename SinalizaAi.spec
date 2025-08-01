import os
from PyInstaller.utils.hooks import collect_submodules, collect_data_files
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

block_cipher = None

project_root = os.path.abspath('.')
mediapipe_datas = collect_data_files('mediapipe', include_py_files=False)

a = Analysis(
    ['src/core/gui.py'],
    pathex=[project_root],
    binaries=[],
    datas=[
        ('models/modelo_libras.pkl', 'models'),
        ('data/ranking.db', 'data'),
        ('src/assets/seguiemj.ttf', 'src/assets'),
        ('src/assets/vitoria.mp3', 'src/assets'),
        ('src/labels.txt', 'src'),
        ('src/config.json', 'src'),
        ('favicon.ico', '.'),  
    ] + mediapipe_datas,
    hiddenimports=(
        collect_submodules('cv2') +
        collect_submodules('pygame') +
        collect_submodules('mediapipe') +
        collect_submodules('sklearn') +
        collect_submodules('joblib') +
        collect_submodules('scipy') +
        collect_submodules('threadpoolctl')
    ),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SinalizaAi',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=os.path.join(project_root, 'favicon.ico')
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SinalizaAi'
)
import os
from PyInstaller.utils.hooks import collect_submodules, collect_data_files
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

block_cipher = None

project_root = os.path.abspath('.')
mediapipe_datas = collect_data_files('mediapipe', include_py_files=False)

a = Analysis(
    ['src/core/gui.py'],
    pathex=[project_root],
    binaries=[],
    datas=[
        ('models/modelo_libras.pkl', 'models'),
        ('data/ranking.db', 'data'),
        ('src/assets/seguiemj.ttf', 'src/assets'),
        ('src/assets/vitoria.mp3', 'src/assets'),
        ('src/labels.txt', 'src'),
        ('src/config.json', 'src'),
        ('favicon.ico', '.'),  
    ] + mediapipe_datas,
    hiddenimports=(
        collect_submodules('cv2') +
        collect_submodules('pygame') +
        collect_submodules('mediapipe') +
        collect_submodules('sklearn') +
        collect_submodules('joblib') +
        collect_submodules('scipy') +
        collect_submodules('threadpoolctl')
    ),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SinalizaAi',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=os.path.join(project_root, 'favicon.ico')
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SinalizaAi'
)
