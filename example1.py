import requests
import os
import time
import random
from lxml.html import etree
from multiprocessing import Pool

# 记录爬取index   TODO：实时记录index,便于暂停与重启
index_1 = 0
index_2 = 0
index_3 = 0

error = open("error_url.txt", "a+")
sess = requests.session()


def get_size(filename):
    if not os.path.exists(filename):
        return 0
    else:
        return os.path.getsize(filename)


def download(url, filename, content_length='', count=0):
    headers = {'Range': 'bytes=%d-' % get_size(filename)}

    if count >= 5:
        error.write(url + "|" + filename + "\n")
        error.flush()
        print(filename + "无法下载")
        return

    try:
        web_log = sess.get(url, stream=True, headers=headers, timeout=20)
        if web_log.status_code == 416:
            print(filename + "下载完成")
            return

        with open(filename, 'ab') as local_file:
            for chunk in web_log.iter_content(chunk_size=1024):
                if chunk:
                    local_file.write(chunk)
                    local_file.flush()

        if not content_length:
            content_length = web_log.headers.get('content-length', '')

        if content_length:
            file_size = get_size(filename)
            if file_size < int(content_length):
                download(url, filename, content_length, count)
            else:
                print(filename + "下载完成")
                return
        else:
            count += 1
            download(url, filename, content_length, count)
    except:
        print(filename, "断点续传")
        count += 1
        time.sleep(1)
        download(url, filename, content_length, count)
        # else:
        #     print(filename + "下载完成")


tree = etree.HTML(open("index.html", encoding="utf-8").read())
basePath = os.path.join(os.getcwd(), "Taxonomic Tree")


def down_main(flag):
    global index_1, index_2, index_3, sess
    print("********logging********")
    sess = requests.session()

    Agent = [
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
        "Mozilla/5.0 (compatible; MSIE 10.6; Windows NT 6.1; Trident/5.0; InfoPath.2; SLCC1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 2.0.50727) 3gpp-gba UNTRUSTED/1.0",
        "Opera/9.25 (Windows NT 6.0; U; en)",
        "Opera/9.80 (Windows NT 6.1; U; es-ES) Presto/2.9.181 Version/12.00",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/531.21.8 (KHTML, like Gecko) Version/4.0.4 Safari/531.21.10",
        "Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/533.17.8 (KHTML, like Gecko) Version/5.0.1 Safari/533.17.8",
        "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/533.19.4 (KHTML, like Gecko) Version/5.0.2 Safari/533.18.5",
        "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-GB; rv:1.9.1.17) Gecko/20110123 (like Firefox/3.x) SeaMonkey/2.0.12",
        "Mozilla/5.0 (Windows NT 5.2; rv:10.0.1) Gecko/20100101 Firefox/10.0.1 SeaMonkey/2.7.1",
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_8; en-US) AppleWebKit/532.8 (KHTML, like Gecko) Chrome/4.0.302.2 Safari/532.8",
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_4; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.464.0 Safari/534.3",
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_5; en-US) AppleWebKit/534.13 (KHTML, like Gecko) Chrome/9.0.597.15 Safari/534.13",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.186 Safari/535.1",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.54 Safari/535.2",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.36 Safari/535.7",
        "Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10.5; en-US; rv:1.9.0.3) Gecko/2008092414 Firefox/3.0.3",
        "Links (2.1pre15; Linux 2.4.26 i686; 158x61)"
    ]

    headers = {
        "User-Agent": random.choice(Agent)
    }

    res = sess.get("https://www.hbw.com/user", headers=headers, timeout=15)

    form_build_id = etree.HTML(res.content).xpath('//input[@name="form_build_id"]/@value')[0]
    print("form_build_id: %s" % form_build_id)

    # 登陆
    data = {
        "name": "**",
        "pass": "****",
        "form_build_id": form_build_id,
        "form_id": "user_login",
        "op": "Log in"
    }

    sess.post("https://www.hbw.com/user", data=data, headers=headers, timeout=15)

    for layer1 in tree.xpath('//ul[@class="orders clearfix"]/li')[index_1:]:
        layer1_name = layer1.xpath('./span/a[@class="name"]/text()')[0]
        layer1_path = os.path.join(basePath, layer1_name)
        print(layer1_name)
        if not os.path.exists(layer1_path):
            os.mkdir(layer1_path)
        for layer2 in layer1.xpath('.//li')[index_2:]:
            id = layer2.xpath('./@id')[0]
            layer2_name = layer2.xpath('./span/a[@class="name"]/text()')[0]
            layer2_path = os.path.join(layer1_path, layer2_name)
            print("--" + layer2_name)
            if not os.path.exists(layer2_path):
                os.mkdir(layer2_path)

            url = "https://www.hbw.com/bird_taxonomies/ajax/species/" + id[3:] + "/38837"
            res = sess.post(url)
            tree1 = etree.HTML(res.text)

            for layer3 in tree1.xpath("//li")[index_3:]:
                href = layer3.xpath("./span/a/@href")[0]
                layer3_name = href.split("/")[-1]
                layer3_path = os.path.join(layer2_path, layer3_name)
                print("----" + layer3_name)
                href1 = "https://www.hbw.com" + href

                if not os.path.exists(layer3_path):
                    # TODO：多次失败后记录该位置然后跳过，避免死链
                    g = 1
                    while g:
                        try:
                            res = sess.get(href1, timeout=10)
                            g = 0
                        except Exception as e:
                            print(e)
                            time.sleep(1)
                            pass

                    os.mkdir(layer3_path)
                    html_out = open(os.path.join(layer3_path, "base.html"), "wb")
                    html_out.write(res.content)
                    html_out.close()

                # time.sleep(random.random())
                url_detail = "https://www.hbw.com/ibc" + href
                g = 1
                while g:
                    try:
                        res_detail = sess.get(url_detail, timeout=10)
                        g = 0
                    except Exception as e:
                        print(e)
                        time.sleep(1)
                        pass

                tree3 = etree.HTML(res_detail.content)

                imgfile = os.path.join(layer3_path, "image")
                pool = Pool(6)
                if not os.path.exists(imgfile):
                    os.mkdir(imgfile)
                for img in tree3.xpath('//a[@class="colorbox"]'):
                    imgurl = img.xpath("./img/@src")[0]
                    pool.apply_async(download, (imgurl, os.path.join(imgfile, imgurl.split("?")[0].split("/")[-1])))
                pool.close()
                pool.join()
                print("图片下载完成")

                videofile = os.path.join(layer3_path, "video")
                pool = Pool(2)
                if not os.path.exists(videofile):
                    os.mkdir(videofile)
                for video in tree3.xpath('//source[@type="video/mp4"]'):
                    videourl = video.xpath("./@src")[0]
                    pool.apply_async(download, (videourl, os.path.join(videofile, videourl.split("/")[-1])))
                pool.close()
                pool.join()
                print("视频下载完成")

                soundfile = os.path.join(layer3_path, "sound")
                pool = Pool(4)
                if not os.path.exists(soundfile):
                    os.mkdir(soundfile)
                for sound in tree3.xpath('//source[@type="audio/mpeg"]/@src'):
                    pool.apply_async(download, (sound, os.path.join(soundfile, sound.split("/")[-1])))
                pool.close()
                pool.join()
                print("音频下载完成")
                index_3 += 1
            index_3 = 0
            index_2 += 1
        index_2 = 0
        index_1 += 1


if __name__ == "__main__":
    flag = 1
    while flag:
        try:
            down_main(flag)
            flag = 0
        except Exception as e:
            print(e)
            time.sleep(3)
            pass
