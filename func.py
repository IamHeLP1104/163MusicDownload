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


def get_playlist_title(cls):
    playlist_inf = requests.get(
        f'https://music.163.com/playlist?id={cls.id}', headers2)
    if playlist_inf.status_code != 200:
        # print(type(self.id))
        if cls.mode == 'gui':
            QMessageBox.warning(cls.ui, '警告', '无效')
        else:
            print('无效')
        return 1
    page_tx = playlist_inf.text
    title = reg.findall(page_tx)[0]
    cls.album_or_playlist_name = title.split(' - ')[0]


def get_playlist_inf(cls):
    res = get_playlist_title(cls)
    if res:
        return 1

    def get_js():
        url = f'https://api.no0a.cn/api/cloudmusic/playlist/{cls.id}'
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

    if not cls.urls and not cls.song_names:

        for song_inf in songs_inf:
            id = song_inf['id']
            url = 'https://link.hhtjim.com/163/' + str(id) + '.mp3'

            song_name = song_inf['name']
            artists_list = [artist['name']
                            for artist in song_inf['artist']]
            artists_name = ', '.join(artists_list)
            full_name = song_name + ' - ' + artists_name + '.mp3'

            cls.song_names.append(full_name)
            cls.urls.append(url)
    else:
        return 1


def get_album_inf(cls):

    def get_inf():
        global songs_information
        try:

            res = requests.get(
                f'http://music.163.com/api/album/{cls.id}?ext=true', headers=headers2)
            dic = res.json()
            name = dic['album']['name']
            songs_inf = dic['album']['songs']
        except KeyError:
            sleep(.5)

            name, songs_inf = get_inf()
        return name, songs_inf
    cls.album_or_playlist_name, songs_information = get_inf()

    # print(dic)

    if not cls.urls and not cls.song_names:
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
            cls.song_names.append(whole_name)
            cls.urls.append(url)
    else:
        return 1


async def download_one_music(cls, url, name=None):
    # print(url, name)
    path = f'Music/{cls.folder_name}/' + name
    if not name:
        name = url.split("/")[-1]
    if os.path.exists(path):
        print(name, "已下载")
        return
    # print(name, "开始")
    # timeout=aiohttp.ClientTimeout(total=60)
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=64, verify_ssl=False)) as session:

        async with session.get(url, headers=headers3) as res:
            # print(res.status)
            if res.status != 200:
                download_one_music(url, name)

            else:
                cont = await res.content.read()

                async with aiofiles.open(path, "wb") as f:

                    await f.write(cont)

    # flag += 1
    # print(5)
    print(name, "结束")


def cut_workers(cls, loop):
    '''
    这个函数意思是避免async超时报错, 把歌曲分成几个Group, 同时顺便促进了PREOGRESSBAR的使用'''
    # print(self.song_names, self.urls)
    asyncio.set_event_loop(loop)
    for one_group in range(1, cls.total_songs_groups + 1):
        cls.downloading_group = one_group
        temp_urls = []
        temp_song_names = []

        for url, song_name in zip(cls.urls[:cls.max_workers], cls.song_names[:cls.max_workers]):

            temp_urls.append(url)
            temp_song_names.append(song_name)
            cls.urls.remove(url)
            cls.song_names.remove(song_name)

        # print(temp_urls, temp_song_names)
        download_music(cls, temp_urls, temp_song_names)
        if cls.mode == 'gui':
            cls.bar_ms.bar_set.emit()
    if cls.mode == 'gui':
        cls.reset_ms.reset.emit()


def get_total_groups(cls):
    cls.total_songs_groups = len(cls.urls) // cls.max_workers + 1
    # print(self.total_songs_groups)


async def create_task(cls, urls, names):
    if names:
        tasks = [asyncio.create_task(download_one_music(
            cls, url, format_name(name))) for url, name in zip(urls, names)]
    else:
        tasks = [asyncio.create_task(
            download_one_music(cls, url)) for url in urls]
    await asyncio.wait(tasks)


def download_music(cls, urls, names=None):
    # t = Thread(target=getProgress)
    # t.start()
    # list_len = len
    cls.folder_name = format_name(cls.album_or_playlist_name)
    if not os.path.exists(f"Music/{cls.folder_name}"):
        os.mkdir(f"Music/{cls.folder_name}")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_task(cls, urls, names))


def format_name(name):
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
