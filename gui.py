from PySide2.QtWidgets import QApplication, QMessageBox, QTableWidgetItem, QProgressBar
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import Qt, QObject, Signal
from threading import Thread
import re
import aiohttp
import aiofiles
import asyncio
import os
from time import sleep
import requests
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


class MySignals(QObject):
    # 定义一种信号，因为有进度条类，此处要2个参数，类型是：QProgressBar、整形数字
    # 调用 emit方法发信号时，传入参数必须是这里指定的参数类型
    # 此处也可分开写两个函数，一个是文本框输出的，一个是给进度条赋值的
    text_print = Signal(QProgressBar, int)


class DownloadMusic():

    def __init__(self):
        self.id = ''
        self.max_workers = 20
        self.song_names = []
        self.album_or_playlist_name = ''
        self.urls = []
        self.an = ''

        self.total_songs_groups = 0

        self.ms = MySignals()  # 引入信号函数
        self.ms.text_print.connect(self.set_bar)  # 将信号传递给主程序中pF函数进行处理
        # 从文件中加载UI定义

        # 从 UI 定义中动态 创建一个相应的窗口对象
        # 注意：里面的控件对象也成为窗口对象的属性了
        # 比如 self.ui.button , self.ui.textEdit
        self.ui = QUiLoader().load('dwnld.ui')
        self.ui.pushButton_3.clicked.connect(lambda: self.begin_download(0))

        self.ui.pushButton_5.clicked.connect(lambda: self.begin_download(1))
        self.ui.show()

    def reset(self):

        self.ui.tableWidget.clearContents()
        self.ui.tableWidget_2.clearContents()
        self.ui.progressBar.reset()
        self.ui.progressBar_2.reset()

    def OneItem(self, tw, row):
        item = QTableWidgetItem(self.song_names[row])
        item.setFlags(Qt.ItemIsEnabled)
        item.setTextAlignment(Qt.AlignCenter)  # 参数名字段不允许修改

        tw.setItem(row, 0, item)

    def setTW(self, tw):
        tw.setRowCount(len(self.urls))
        for row in range(len(self.urls)):
            self.OneItem(tw, row)

    def begin_download(self, kind):
        if kind == 0:
            try:
                self.id = int(self.ui.lineEdit.text())
            except ValueError:
                QMessageBox.warning(self.ui, '警告', '无效')
            else:

                res = self.get_playlist_inf()
                if res:
                    return
                tw = self.ui.tableWidget

        elif kind == 1:
            try:
                self.id = int(self.ui.lineEdit_2.text())
            except ValueError:
                QMessageBox.warning(self.ui, '警告', '无效')
            else:
                res = self.get_album_inf()
                if res:
                    return
                tw = self.ui.tableWidget_2
        self.get_total_groups(kind)
        if self.id:

            self.setTW(tw)
            if res:
                QMessageBox.warning(self.ui, '警告', '等待当前任务完成')
            loop = asyncio.new_event_loop()
            worker = Thread(target=self.cut_workers, args=(loop, ))
            worker.start()

        else:
            QMessageBox.warning(self.ui, '警告', '未输入')
            return

    def cut_workers(self, loop):
        # print(self.song_names, self.urls)
        asyncio.set_event_loop(loop)
        for i in range(1, self.total_songs_groups + 1):
            temp_urls = []
            temp_song_names = []

            for url, song_name in zip(self.urls[:self.max_workers], self.song_names[:self.max_workers]):

                temp_urls.append(url)
                temp_song_names.append(song_name)
                self.urls.remove(url)
                self.song_names.remove(song_name)

            # print(temp_urls, temp_song_names)
            self.download_music(temp_urls, temp_song_names)
            self.ms.text_print.emit(self.bar, i)
        self.reset()

    def get_total_groups(self, kind):
        self.total_songs_groups = len(self.urls) // self.max_workers + 1
        # print(self.total_songs_groups)

        if kind == 0:
            self.bar = self.ui.progressBar
        elif kind == 1:
            self.bar = self.ui.progressBar_2
        self.bar.setRange(0, self.total_songs_groups)

    def get_playlist_title(self, id):
        playlist_inf = requests.get(
            f'https://music.163.com/playlist?id={id}', headers2)
        if playlist_inf.status_code != 200:
            # print(type(self.id))
            QMessageBox.warning(self.ui, '警告', '无效')

            return 1
        page_tx = playlist_inf.text
        title = reg.findall(page_tx)[0]
        self.album_or_playlist_name = title.split(' - ')[0]

    def get_album_inf(self):

        res = requests.get(
            f'http://music.163.com/api/album/{self.id}?ext=true', headers=headers2)
        if res.status_code != 200:
            QMessageBox.warning(self.ui, '警告', '无效')

            return 1

        def get_json():
            global songs_information
            dic = res.json()
            self.album_or_playlist_name = dic['album']['name']
            songs_information = dic['album']['songs']
        try:
            get_json()

        except KeyError:
            QMessageBox.warning(self.ui, '警告', '无效')

            return 1

        # print(dic)

        if not self.urls and not self.song_names:
            for song_information in songs_information:
                # print(i['id'], ']i['name)
                artists_names_list = []
                artists_inf = song_information['artists']
                for artist_inf in artists_inf:
                    artist_name = artist_inf['name']
                    artists_names_list.append(artist_name)

                id = song_information['id']
                url = 'https://link.hhtjim.com/163/' + str(id) + '.mp3'
                whole_name = song_information['name'] + \
                    ' - ' + ', '.join(artists_names_list) + '.mp3'
                # print(id, url)
                # url = res.json()['data'][0]['urls']['original']
                self.song_names.append(whole_name)
                self.urls.append(url)
        else:
            return 1

    def get_playlist_inf(self):
        res = self.get_playlist_title(self.id)
        if res:
            return 1

        def get_js():
            url = f'https://api.no0a.cn/api/cloudmusic/playlist/{self.id}'
            # print(url)
            js_res = requests.get(url, headers1)
            # print(js_res.text)
            try:
                js_res = js_res.json()
            except requests.exceptions.JSONDecodeError:
                return 1
            songs_inf = js_res['results']
            if len(songs_inf) == 1:

                sleep(0.3)
                songs_inf = get_js()
            return songs_inf
        songs_inf = get_js()

        if not self.urls and not self.song_names:

            for song_inf in songs_inf:
                id = song_inf['id']
                url = 'https://link.hhtjim.com/163/' + str(id) + '.mp3'

                song_name = song_inf['name']
                artists_list = [artist['name']
                                for artist in song_inf['artist']]
                artists_name = ', '.join(artists_list)
                full_name = song_name + ' - ' + artists_name + '.mp3'

                self.song_names.append(full_name)
                self.urls.append(url)
        else:
            return 1

    def format_name(self, name):
        name = name.replace('\\', '')
        name = name.replace('/', '')
        name = name.replace(':', '：')
        name = name.replace('?', '？')
        name = name.replace('*', '-')
        name = name.replace('<', '《')
        name = name.replace('>', '》')
        name = name.replace('|', '.')
        name = name.replace('"', '\'\'')
        return name

    async def download_one_music(self, url, name=None):
        # print(url, name)
        if not name:
            name = url.split("/")[-1]
        # print(name, "开始")
        # timeout=aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession() as session:

            async with session.get(url, headers=headers3) as res:
                # print(res.status)
                if res.status != 200:
                    self.download_one_music(url, name)

                else:
                    cont = await res.content.read()
                    path = f'Music/{self.an}/' + name

                    async with aiofiles.open(path, "wb") as f:

                        await f.write(cont)

        # flag += 1
        # print(5)
        print(name, "结束")

    async def create_task(self, urls, names):
        if names:
            tasks = [asyncio.create_task(self.download_one_music(
                url, self.format_name(name))) for url, name in zip(urls, names)]
        else:
            tasks = [asyncio.create_task(
                self.download_one_music(url)) for url in urls]
        await asyncio.wait(tasks)

    def download_music(self, urls, names=None):
        # t = Thread(target=getProgress)
        # t.start()
        # list_len = len
        self.an = self.format_name(self.album_or_playlist_name)
        if not os.path.exists(f"Music/{self.an}"):
            os.mkdir(f"Music/{self.an}")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.create_task(urls, names))

    def set_bar(self, bar, _int):
        bar.setValue(_int)


app = QApplication([])

stats = DownloadMusic()
app.exec_()
