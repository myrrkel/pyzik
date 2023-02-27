
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread


class LoadAlbumFilesThread(QThread):
    """Read datas from files in the album folder"""

    do_stop = False
    album = None
    player = None
    images_loaded = pyqtSignal(int, name="imagesLoaded")
    tracks_loaded = pyqtSignal(int, name="tracksLoaded")

    def run(self):
        self.do_stop = False
        self.album.get_images()
        if self.do_stop:
            return
        self.album.get_cover()
        self.images_loaded.emit(1)
        if self.do_stop:
            return
        self.album.get_tracks()
        self.tracks_loaded.emit(1)
        return

    def stop(self):
        self.do_stop = True
        self.album.set_do_stop()
