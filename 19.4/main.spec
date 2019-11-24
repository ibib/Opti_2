# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


added_files = [
         ( 'gui.ui', '.'),
         ( 'config.ini', '.' ),
		 ( 'settings.ui', '.'),
		 ( 'pyzdde', 'pyzdde'),
		 ( 'AHK', 'AHK'),
		 ( 'Convert_to_NSGroup.ahk', '.'),
		 ( 'Convert_to_NSGroup_2.ahk', '.'),
		 ( 'help.ui', '.' ),
		 ( 'optimize.ahk', '.' ),
		 ( 'optimize_2.ahk', '.' ),
		 ( 'Export_to_CAD_7.ahk', '.' ),
		 ( 'Export_to_CAD_10.ahk', '.' ),
		 ( 'ray_trace.ahk', '.' )
         ]

a = Analysis(['main.py'],
             pathex=['C:\\Users\\Jannes_S5\\Dropbox\\IPeG\\zemax_gui'],
             binaries=[],
             datas=added_files,
             hiddenimports=['pyzdde'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='main')
