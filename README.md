

# 163MusicDownload 
![Github stars](https://img.shields.io/badge/any_text-you_like-blue)
## 安装Python
[根据此网站教程安装Python](http://www.liaoxuefeng.com/wiki/001374738125095c955c1e6d8bb493182103fac9270762a000/001374738150500472fd5785c194ebea336061163a8a974000)
注意安装的版本是 **python3**

强制使用 python3, 从我做起

## 使用方法 
### 1.安装库，在终端输入以下命令
    pip install requests
    pip install aiohttp
    pip install aiofiles
### 2.在某个网易云音乐歌单或专辑网址上复制ID, 这些URL应类似于[https://music.163.com/#/playlist?id=2189465719](https://music.163.com/#/playlist?id=2189465719), 只要复制id=后面的一串数字就行了.
#### 有两种方法，第一种,在终端输入以下命令(第一行是下载专辑的，第二行是下载歌单的):
    python cmd.py -a (id)
    python cmd.py -p (id)
#### 第2种：直接运行gui.py,不过要额外安装pyside2（不建议，这个包太大了，200mb多，还只支持python3.9之前）
    pip install Pyside2
### 失败了多试几次, 因为有极少数的时候会出BUG

Enjoy it !

### 版权问题
如果涉及版权问题，项目将立刻关闭。
自己为百度音乐会员, 该项目为方便自己而做
