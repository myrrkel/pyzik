# Pyzik Player

Pyzik Player finds datas from albums directories name and saves it in database. 

ID3 tags are only used when there is no over option to get albums information.

#### What's the point?

Even if you have a very big music storage, all albums are referenced very quickly.

Just tell where are your repositories and play your music.


<img src="https://raw.githubusercontent.com/myrrkel/pyzik/master/screenshot.png" alt="pyzik" />



## Pyzik script command line: 

Start the project:

    python3 ./src/pyzik.py
    
Parameters:

    -d, --debug:       Enable debug mode
    -s, --style:       Set Qt Style (Windows, Fusion...)
    -p, --db-path:     Set the database file path (~/.local/share/pyzik/data/pyzik.db)
    -h, --help:        Display help


To install requirements:

    pip install -r requirements.txt

## Install on Linux

    wget https://github.com/myrrkel/pyzik/releases/download/v0.3-beta/pyzik-0.3.linux-86_64-standalone.tar.gz
    tar -zxvf pyzik-0.3.linux-86_64-standalone.tar.gz


## To build the project: 

For Linux:

    pyinstaller -y pyzik.spec
    tar -zcvf dist/pyzik-0.3.linux-86_64-standalone.tar.gz dist/pyzik


To make a Windows MSI Installer:

    python setup.py bdist_msi

To make a Windows EXE Installer:

    pyinstaller -y pyzik.spec
    "C:\Program Files (x86)\NSIS\makensisw.exe" pyzik.nsi
    ( install NSIS from https://nsis.sourceforge.io )


## News
+ Grab covers from Google Image
+ Full screen mode with current track and cover art
+ Radio finder (with RadioBrower, Tunein, Dar or Dirble)
+ Played tracks and radio history
+ Music style filter
+ Playing radio without ads
+ Reading tags
+ Language selector
+ Generating random M3U playlist
+ Correcting folder's name according ID3 tags
+ Import albums from dirty directories like 'Downloads' to music storage

## Coming soon

+ Collecting track lyrics from web
+ USB Music Player Manager: Fill a USB storage with music you like
+ Music Base Information (Number of artist, albums...)
+ Filters in history view
+ Web Radio Manager
+ Explore Event tool
+ Album information, update and delete tools


## Thanks

https://www.videolan.org for LibVLC

https://olivieraubert.net for Python VLC binding

http://www.radio-browser.info for radio search api


