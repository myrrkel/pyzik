# -*- mode: python -*-

block_cipher = None



a = Analysis(['src/pyzik.py'],
             pathex=['src', '/home/myrrkel/workspace/pyzik'],
             binaries=[],
             datas=[],
             hiddenimports=['/usr/lib/x86_64-linux-gnu/vlc'],
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
          exclude_binaries=True,
          name='pyzik',
          debug=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               Tree('src/img', prefix='img'),
               Tree('src/darkStyle', prefix='darkStyle'),
               Tree('src/translation', prefix='translation'),
               Tree('/usr/lib/x86_64-linux-gnu/vlc', prefix='vlc'),
               strip=False,
               upx=True,
               name='pyzik')
