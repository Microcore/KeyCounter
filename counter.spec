# -*- mode: python -*-
from PyInstaller import compat

block_cipher = None


a = Analysis(['counter.py'],
             pathex=['.'],
             binaries=None,
             datas=None,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='KeyCounter',
          debug=False,
          strip=False,
          upx=True,
          console=False )

if compat.is_darwin:
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        name='KeyCounter.Collect'
    )
    app = BUNDLE(
        coll,
        name='KeyCounter.app',
        icon=os.path.join(compat.getcwd(), 'resources', 'Unchecked Circle Filled.icns'),
        bundle_identifier='org.microcore.keycounter',
        info_plist={
            'NSHighResolutionCapable': 'True',
            # TODO i18n app name
            'CFBundleName': 'KeyCounter',
            # 'CFBundleVersion': '',
            'LSApplicationCategoryType': 'Productivity',
            'LSMinimumSystemVersion': '10.10',
            'NSHumanReadableCopyright': 'Copyright © 2016 Microcore Team All rights reserved.',
        }
    )
