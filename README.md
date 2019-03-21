# pyzik

<img src="https://raw.githubusercontent.com/myrrkel/pyzik/master/screenshot.png" alt="pyzik" />

Pyzik explores big music directories like:

                                    ./Rock/Artist1 - [1965] - Album1
                                    ./Rock/Artist1 - [1967] - Album2
                                    ./Rock/Artist2 - Album2 (1972)
                                    ...
                                    ./Blues/Artist3 - Album4
                                    ...

or

                                    ./Artist/1972 - Album1
                                    ./Artist/1975 - Album2
                                    ./Artist2/1967 - Album1
                                    ./Artist2/1968 - Album2




Pyzik finds datas from albums directories name and saves it in database. 

So you can find your music quickly, and play it.


# To start the project use the command line: 

install requirements:

    pip install -r requirements.txt

start the project:

    python3 ./src/pyzik.py


# Install on Linux

    wget https://github.com/myrrkel/pyzik/releases/download/v0.3-beta/pyzik-0.3.linux-86_64-standalone.tar.gz
    tar -zxvf pyzik-0.3.linux-86_64-standalone.tar.gz


# To build the project: 

For Linux:

    pyinstaller -y pyzik.spec
    tar -zcvf dist/pyzik-0.3.linux-86_64-standalone.tar.gz dist/pyzik

To make an Windows MSI Installer:

    python setup.py bdist_msi

To make an Windows EXE Installer:

    pyinstaller -y pyzik.spec
    "C:\Program Files (x86)\NSIS\makensisw.exe" pyzik.nsi
    ( install NSIS from https://nsis.sourceforge.io )


# News
+ Grab covers from Google Image
+ Full screen mode with current track and cover art
+ Radio finder (from RadioBrower, Tunein, Dar and Dirble)
+ Played tracks and radio history
+ Music style filter
+ Playing radio without ads
+ Reading tags
+ Language selector


# Coming soon:
+ Generating random M3U playlist
+ Correcting folder's name acording ID3 tags
+ Collecting track title and lyrics from web




