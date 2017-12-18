import requests
import os
from multiprocessing.dummy import Pool as thread_pool

tp = thread_pool(10)

def download(url, filename, content_length=''):

    def get_size(filename):
        if not os.path.exists(filename):
            try:
                f = open(filename, 'a+')
                f.close()
            except:
                path = filename.split('\\')
                filename = "/".join(path[:-1]) + '/' + path[-1][-20:]
            return filename, 0
        else:
            return filename, os.path.getsize(filename)

    filename, filesize = get_size(filename)
    header = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
        'Range': 'bytes=%d-' % filesize
    }
    try:
        web_log = requests.get(url, stream=True, headers=header, timeout=30)
        print(web_log)
        if web_log.status_code == 416:
            print(filename + "下载完成")
            return

        with open(filename, 'ab+') as local_file:
            for chunk in web_log.iter_content(chunk_size=256):
                if chunk:
                    local_file.write(chunk)
                    local_file.flush()

        download(url, filename, content_length)

    except Exception as e:
        print(e)
        download(url, filename, content_length)


with open("error_url.txt") as f:
    for line in f:
        line = line.strip().split("|")
        url = line[0]
        path = line[1]
        tp.apply_async(download, (url, path))
tp.close()
tp.join()
