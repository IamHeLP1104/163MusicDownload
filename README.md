

# 163MusicDownload ![Github stars](https://img.shields.io/badge/HeLP-Music-blue)
免费下载网易云音乐的歌单🎧🎵
## EasyToStart
1.安装Python[根据此网站教程安装Python](http://www.liaoxuefeng.com/wiki/001374738125095c955c1e6d8bb493182103fac9270762a000/001374738150500472fd5785c194ebea336061163a8a974000)
注意安装的版本是 **python3**
2.安装库，在终端输入以下命令
    pip install requests
    pip install aiohttp
    pip install aiofiles
3.在某个网易云音乐歌单或专辑网址上复制ID, 这些URL应类似于[https://music.163.com/#/playlist?id=2189465719](https://music.163.com/#/playlist?id=2189465719), 只要复制id=后面的一串数字就行了.
4.在终端输入以下命令(第一行是下载专辑的，第二行是下载歌单的):
    python cmd.py -a (id)
    python cmd.py -p (id)
### 失败了多试几次, 因为有极少数的时候会出BUG

Enjoy it !

### 版权问题
如果涉及版权问题，项目将立刻关闭。
