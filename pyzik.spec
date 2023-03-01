# -*- mode: python -*-
import sys


block_cipher = None



if sys.platform.startswith('linux'):


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
                   Tree('src/translation', prefix='translation'),
                   Tree('/usr/lib/x86_64-linux-gnu/vlc', prefix='vlc'),
                   strip=False,
                   upx=True,
                   name='pyzik')


elif sys.platform.startswith('win'):

    a = Analysis(['src\\pyzik.py'],
                 pathex=['src', 'venv', 'C:\\Windows\\System32\\downlevel', 'C:\\Users\\mp05.octave\\Documents\\Python\\pyzik','C:\\Program Files (x86)\\VideoLAN\\VLC'],
                 binaries=[],
                 datas=[('C:\\Program Files (x86)\\VideoLAN\\VLC\\libvlc.dll','.')],
                 hiddenimports=['C:\\Program Files (x86)\\VideoLAN\\VLC','C:\\Program Files (x86)\\VideoLAN\\VLC\\plugins'],
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
              console=False )
    coll = COLLECT(exe,
                   a.binaries,
                   a.zipfiles,
                   a.datas,
                   Tree('src\\img', prefix='img'),
                   Tree('src\\translation', prefix='translation'),
                   Tree('C:\\Program Files (x86)\\VideoLAN\\VLC\\plugins', prefix='plugins'),
                   strip=False,
                   upx=True,
                   name='pyzik')


#Tree('C:\\Program Files (x86)\\VideoLAN\\VLC', prefix='VLC'),
#'C:\\Program Files (x86)\\VideoLAN\\VLC\\libvlccore.dll','C:\\Program Files (x86)\\VideoLAN\\VLC\\libvlc.dll'
#Tree('C:\\Program Files (x86)\\VideoLAN\\VLC\\plugins', prefix='plugins'),