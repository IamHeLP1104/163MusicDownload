from PySide2.QtWidgets import QApplication, QMessageBox
from PySide2.QtUiTools import QUiLoader
from threading import Thread
import re
import aiohttp
import aiofiles
import asyncio
import os
from time import sleep
import requests
headers ={ 
    # 'referer': 'https://bing.ioliu.cn/',
    # "Host": "bing.ioliu.cn",
    'Host': 'm8.music.126.net',
    "User-Agent": 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Mobile Safari/537.36 Edg/92.0.902.67',
    'Cookie': '__gads=ID=95fc96e63d3645a1-226064c90cd600d5:T=1661691636:RT=1661691636:S=ALNI_MavLvODNnavCXaP4h1tKY02YB7cxQ; __gpi=UID=0000092d25d19805:T=1661691636:RT=1661691636:S=ALNI_MYgnl7fRFaQEAG8XQOv-US8gs9_Sg',
    'Connection': 'keep-alive',
}
headers1 ={
    'Host': 'api.no0a.cn',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Cookie': 'Hm_lvt_f41620af9755d9c22a24ca27a323e40b=1661692758; Hm_lpvt_f41620af9755d9c22a24ca27a323e40b=1661692758',
    'Upgrade-Insecure-Requests': 1,
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'If-None-Match': 'W/"551-7c+a+njd9Hbe4FKoJpbULfsFeAk"',
    'TE': 'trailers',
}
headers2 = {
    'Host': 'music.163.com',
    # 'Connection': 'keep-alive',
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0',
}
headers4 = {
    'Host': 'music.163.com',
    # 'Connection': 'keep-alive',
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0',

    'Cookie': 'JSESSIONID-WYYY=EcbWXn8zBxDpIdjhpj%5CtzFPJpHektI5uoxptwVZdJX8kZ5ibyDDrK%5CGm2tInOr7MxMZB2jpz9bNHC9ocvTHOXrn1%5Cbv%2B5b3OryTbjiWQuMRtZYXf6JB2pzfSWnbE1M1hfZ2xDJQ2%5CrvSrzNtQjJu3266jDbqp7BIINMVBAE1F0ekHoF7%3A1662730781709; _iuqxldmzr_=32; _ntes_nnid=fef78cc22ecc571b6c270c401cc34441,1661435512428; _ntes_nuid=fef78cc22ecc571b6c270c401cc34441; NMTID=00O2WR0QV5B0YElBUvvkPZeQk1dg3EAAAGC1UYNOQ; WEVNSM=1.0.0; WNMCID=uclqkm.1661435513719.01.0; WM_NI=p5MjtnlZ2WYsV01SCnJmHZS7c2lIwDxOeJ0jAzIlV7XouVzBAc5ZGnxzdtzVWqXqCywGd…cAst48TOu1KpRYY9y09TcZj4G249bRWlLyK5lRzYWmtvm1UGU%3D; YD00000558929251%3AWM_NIKE=9ca17ae2e6ffcda170e2e6eea7b345a1ac86adb360af9a8eb7c84a979e8f87d154a2b3988cb553ad9fafb4cd2af0fea7c3b92ab8b000a8c250a192a1dacc538c929b9be93aae8ae58ad945aa8700dae748fbea8eb6b239a8b0a0a5e47fb5b68e8bc8739ba6ffa5f2529ba80092e13392b88fb1fb7bf19584aaef79adae9886bc33b0ef8d94e24bb1acfcd9d745b7ef8591d1539be7b7d1bc60a186a6d5c63af8e7aeb3d66890a785d6ef5aba87998ef77eafef9ba8d837e2a3; YD00000558929251%3AWM_TID=z2sKnihePb5AEEFAEFeRXKjS06Y9FLXJ'.encode("utf-8").decode("latin1"),
}
header3 = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0',
}
reg = re.compile("<title>(.*?)</title>", re.S)


class DownloadMusic():

    def __init__(self):
        self.id = ''
        self.max_workers = 20
        self.song_names = []
        self.album_or_playlist_name = ''
        self.urls = []
        self.an = ''
        # 从文件中加载UI定义

        # 从 UI 定义中动态 创建一个相应的窗口对象
        # 注意：里面的控件对象也成为窗口对象的属性了
        # 比如 self.ui.button , self.ui.textEdit
        self.ui = QUiLoader().load('dwnld.ui')

        self.ui.lineEdit.returnPressed.connect(lambda: self.saveID(0))
        self.ui.lineEdit_2.returnPressed.connect(lambda: self.saveID(1))

        self.ui.pushButton_2.clicked.connect(lambda: self.saveID(0))
        self.ui.pushButton_4.clicked.connect(lambda: self.saveID(1))
        self.ui.pushButton_3.clicked.connect(lambda: self.beginDownload(0))

        self.ui.pushButton_5.clicked.connect(lambda: self.beginDownload(1))
        self.ui.show()
    def testGetUrlsNames(self, loop):
        asyncio.set_event_loop(loop)
        print(self.song_names, self.urls)    

        
    def saveID(self, kind):
        if kind == 0:
            self.id = self.ui.lineEdit.text()
        if kind == 1:
            self.id = self.ui.lineEdit_2.text()
        



    def beginDownload(self, kind):
        if self.id:
            if kind == 0:
                res = self.getPlaylistInf()
            if kind == 1:
                res = self.getAlbumInf()
            if res:
                QMessageBox.warning(self.ui, '警告','等待当前任务完成')     
            loop = asyncio.new_event_loop()
            worker = Thread(target=self.cutWorkers, args=(loop, kind))
            worker.start()
        else:
            QMessageBox.warning(self.ui, '警告','未输入')
            return
    def cutWorkers(self, loop, kind):
        print(self.song_names, self.urls)  
        asyncio.set_event_loop(loop)    

        list_len = len(self.urls) // self.max_workers + 1

        if kind == 0:
            bar = self.ui.progressBar
        elif kind == 1:
            bar = self.ui.progressBar_2
        bar.setRange(0, list_len)
        for i in range(1, list_len + 1):
            temp_urls = []
            temp_song_names = []
            
            for url, song_name in zip(self.urls[:self.max_workers], self.song_names[:self.max_workers]):
                
                temp_urls.append(url)
                temp_song_names.append(song_name)
                self.urls.remove(url)
                self.song_names.remove(song_name)
            bar.setValue(i)
            # print(temp_urls, temp_song_names) 
            self.downloadMusic(temp_urls, temp_song_names)    
    def getPlaylistTitle(self, id):
        playlist_inf = requests.get(f'https://music.163.com/playlist?id={id}', headers2)
        if playlist_inf.status_code != 200:
            QMessageBox.warning(self.ui, '警告', '无效')

            return
        page_tx = playlist_inf.text
        title = reg.findall(page_tx)[0]
        self.album_or_playlist_name = title
    def getAlbumInf(self):

        res = requests.get(f'http://music.163.com/api/album/{self.id}?ext=true', headers=headers4)
        # print(res)
        if res.status_code != 200:
            QMessageBox.warning(self.ui, '警告', '无效')

            return



        dic = res.json()
        # print(dic)
        self.album_or_playlist_name = dic['album']['name']
        songs_information = dic['album']['songs']
        if not self.urls and not self.song_names:
            for i in songs_information:
                # print(i['id'], ']i['name)
                id = i['id']
                url = 'https://link.hhtjim.com/163/' + str(id) +'.mp3'
                name = i['name'] + '.mp3'
                print(id, url)
                # url = res.json()['data'][0]['urls']['original']
                self.song_names.append(name)
                self.urls.append(url)
        else:
            return 1
    def getPlaylistInf(self):
        self.getPlaylistTitle(self.id)
        def get_js():
            url = f'https://api.no0a.cn/api/cloudmusic/playlist/{self.id}'
            # print(url)
            js_res = requests.get(url, headers1)
            # print(js_res.text)
            js_res = js_res.json()
            songs_inf = js_res['results']
            if len(songs_inf) == 1:
                sleep(1)
                songs_inf= get_js()
            return songs_inf
        songs_inf = get_js()

        if not self.urls and not self.song_names:

            for song_inf in songs_inf:
                id = song_inf['id']
                url = 'https://link.hhtjim.com/163/' + str(id) +'.mp3'

                song_name = song_inf['name']
                artists_list = [artist['name'] for artist in song_inf['artist']]
                artists_name = ','.join(artists_list)
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

    async def downloadOneMusic(self, url, name=None):
        print(url, name)
        if not name:
            name = url.split("/")[-1]
        # print(name, "开始")
        async with aiohttp.ClientSession() as session:

            async with session.get(url, headers=headers) as res:
                # print(res.status)
                if res.status != 200:
                    self.downloadOneMusic(url, name)

                else:
                    cont = await res.content.read()
                    path = f'./{self.an}/' + name

                    async with aiofiles.open(path, "wb") as f:

                        await f.write(cont)
                    
        # flag += 1
        # print(5)
        print(name, "结束")
    async def main(self, urls, names):
        if names:
            tasks = [asyncio.create_task(self.downloadOneMusic(url, self.format_name(name))) for url, name in zip(urls, names)]
        else:
            tasks = [asyncio.create_task(self.downloadOneMusic(url)) for url in urls]
        await asyncio.wait(tasks)
        
    def downloadMusic(self, urls, names=None):
        # t = Thread(target=getProgress)
        # t.start()
        # list_len = len
        self.an = self.format_name(self.album_or_playlist_name)
        if not os.path.exists(f"./{self.an}"):
            os.mkdir(f"./{self.an}")
        loop = asyncio.get_event_loop()  
        loop.run_until_complete(self.main(urls, names))
        # en = True
        # print('100%/100%')
        # t.join()  



          
    

app = QApplication([])

stats = DownloadMusic()
app.exec_()
'''
def downloadOneMusic(url, name=None):
    print(url, name)
    if not name:
        name = url.split("/")[-1]
    # print(name, "开始")

    res = requests.get(url, headers=headers)
    if 200!= 200:
        downloadOneMusic(url, name)

    else:
        cont = res.content
        path = name

        with open(path, "wb") as f:

            f.write(cont)
downloadOneMusic(
        'https://link.hhtjim.com/163/1242476.mp3',
        'What Planet Are You On？ (deadmau5 Remix) - Bodyrox,Luciana,deadmau5.mp3'
)
'''