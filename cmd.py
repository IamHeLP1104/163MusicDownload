from func import get_playlist_inf, get_album_inf, get_total_groups, cut_workers
from threading import Thread
import os
import sys
import asyncio
args = sys.argv


class DownloadMusic():

    def __init__(self):
        self.mode = 'cmd'
        self.id = ''
        self.max_workers = 20
        self.song_names = []
        self.album_or_playlist_name = ''
        self.urls = []
        self.folder_name = ''

        self.total_songs_groups = 0

    def begin_download(self):
        print('Begin to download')
        print('Just waiting...')
        get_total_groups(self)
        loop = asyncio.new_event_loop()
        worker = Thread(target=cut_workers, args=(self, loop, ))
        worker.start()


def layout_help():
    help_content = '''
    -h : View this help page
    -a or --album : Download one album
    -p or --playlist : Download one playlist
    '''.format(sys.argv[0])
    print(help_content)
    exit()


if __name__ == '__main__':

    if len(args) == 3:
        dl = DownloadMusic()
        dl.id = args[2]
        if args[1] == '-a' or '--album':
            get_album_inf(dl)
            print(dl.album_or_playlist_name)
        if args[1] == '-p' or '--playlist':
            get_playlist_inf(dl)
        else:
            layout_help()
        dl.begin_download()
    else:
        layout_help()
