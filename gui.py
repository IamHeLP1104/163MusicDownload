from func import get_playlist_inf, get_album_inf, get_total_groups, cut_workers

from PySide2.QtWidgets import QApplication, QMessageBox, QTableWidgetItem
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import Qt, QObject, Signal

from threading import Thread
import re
import asyncio
from time import sleep

headers1 = {
    'Host': 'api.no0a.cn',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0',
}
headers2 = {
    'Host': 'music.163.com',
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0',
}
headers3 = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0',
}
reg = re.compile("<title>(.*?)</title>", re.S)


class ProgressBarSignals(QObject):
    bar_set = Signal()


class ResetSignals(QObject):
    reset = Signal()


class DownloadMusic():

    def __init__(self):
        self.mode = 'gui'
        self.id = ''
        self.max_workers = 20
        self.song_names = []
        self.album_or_playlist_name = ''
        self.urls = []
        self.folder_name = ''

        self.total_songs_groups = 0

        ### 这4行作用是为了在子线程中更改UI, 否则会报错
        self.bar_ms = ProgressBarSignals()
        self.bar_ms.bar_set.connect(self.set_bar)
        self.reset_ms = ResetSignals()
        self.reset_ms.reset.connect(self.reset)

        self.ui = QUiLoader().load('UI/dwnld.ui')
        self.ui.setFixedSize(self.ui.width(), self.ui.height())

        self.ui.pushButton_3.clicked.connect(lambda: self.begin_download(0))
        self.ui.pushButton_5.clicked.connect(lambda: self.begin_download(1))
        self.ui.show()

    def reset(self):
        self.bar.reset()
        self.tw.clearContents()
        QMessageBox.information(
            self.ui, 'Music', '下载完毕')

        self.id = ''
        self.song_names = []
        self.album_or_playlist_name = ''
        self.urls = []
        self.folder_name = ''
        self.total_songs_groups = 0

    def OneItem(self, tw, row):
        item = QTableWidgetItem(self.song_names[row])
        item.setFlags(Qt.ItemIsEnabled)
        item.setTextAlignment(Qt.AlignCenter)  # 参数名字段不允许修改

        tw.setItem(row, 0, item)

    def setTW(self):
        self.tw.setRowCount(len(self.urls))
        for row in range(len(self.urls)):
            self.OneItem(self.tw, row)

    def begin_download(self, kind):
        self.kind = kind
        if self.kind == 0:
            try:
                self.id = int(self.ui.lineEdit.text())
            except ValueError:
                QMessageBox.warning(self.ui, '警告', '无效')
            else:

                res = get_playlist_inf(self)
                if res:
                    return
                self.tw = self.ui.tableWidget

        elif self.kind == 1:
            try:
                self.id = int(self.ui.lineEdit_2.text())
            except ValueError:
                QMessageBox.warning(self.ui, '警告', '无效')
            else:
                res = get_album_inf(self)
                if res:
                    return
                self.tw = self.ui.tableWidget_2
        get_total_groups(self)

        if self.kind == 0:
            self.bar = self.ui.progressBar
        elif self.kind == 1:
            self.bar = self.ui.progressBar_2
        self.bar.setRange(0, self.total_songs_groups)
        if self.id:

            self.setTW()
            if res:
                QMessageBox.warning(self.ui, '警告', '等待当前任务完成')
            loop = asyncio.new_event_loop()
            worker = Thread(target=cut_workers, args=(self, loop, ))
            worker.start()

        else:
            QMessageBox.warning(self.ui, '警告', '未输入')
            return

    def set_bar(self):
        self.bar.setValue(self.downloading_group)

    def warn(self):
        QMessageBox.warning(self.ui, '警告', '无效')


app = QApplication([])

stats = DownloadMusic()
app.exec_()
