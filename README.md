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

    python3 ./pyzik/src/pyzik.py


# To build on Linux or Windows: 

    pyinstaller -y pyzik.spec

#To make an MSI Installer

    python setup.py bdist_msi

#To make an EXE Installer

    "C:\Program Files (x86)\NSIS\makensisw.exe" pyzik.nsi
    ( install NSIS from https://nsis.sourceforge.io )

# News
+ Played tracks and radio history
+ Music style filter
+ Playing radio without ads
+ Reading tags
+ Language selector
+ Displaying covers art


# Coming soon:
+ Full screen mode with current track and cover art.
+ Radio manager
+ Correcting folder's name acording ID3 tags
+ Collecting cover art and track list from web




