import random
import time

import requests
from PyQt5.QtWidgets import QMessageBox
from bs4 import BeautifulSoup


class QueryWords:
    @staticmethod
    def rand_header():
        head_connection = ['Keep-Alive', 'close']
        head_accept = ['text/html, application/xhtml+xml, */*']
        head_accept_language = ['zh-CN,fr-FR;q=0.5', 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3']
        head_user_agent = ['Opera/8.0 (Macintosh; PPC Mac OS X; U; en)',
                           'Opera/9.27 (Windows NT 5.2; U; zh-cn)',
                           'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Win64; x64; Trident/4.0)',
                           'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)',
                           'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.2; .NET4.0C; .NET4.0E)',
                           'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.2; .NET4.0C; .NET4.0E; QQBrowser/7.3.9825.400)',
                           'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; BIDUBrowser 2.x)',
                           'Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070309 Firefox/2.0.0.3',
                           'Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070803 Firefox/1.5.0.12',
                           'Mozilla/5.0 (Windows; U; Windows NT 5.2) Gecko/2008070208 Firefox/3.0.1',
                           'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.12) Gecko/20080219 Firefox/2.0.0.12 Navigator/9.0.0.6',
                           'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36',
                           'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; rv:11.0) like Gecko)',
                           'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0 ',
                           'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Maxthon/4.0.6.2000 Chrome/26.0.1410.43 Safari/537.1 ',
                           'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.92 Safari/537.1 LBBROWSER',
                           'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36',
                           'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/3.0 Safari/536.11',
                           'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
                           'Mozilla/5.0 (Macintosh; PPC Mac OS X; U; en) Opera 8.0'
                           ]
        header = {
            'Connection': head_connection[0],
            'Accept': head_accept[0],
            'Accept-Language': head_accept_language[1],
            'User-Agent': head_user_agent[random.randrange(0, len(head_user_agent))]
        }
        return header

    @staticmethod
    def get_current_time():
        # 获取当前时间
        return time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime(time.time()))

    # def get_url(self, url, dialog_object,tries_num=5, sleep_time=0, time_out=10, max_retry=5, is_proxy=0, proxy=None,
    def get_url(self, url, dialog_object, time_out=10, is_proxy=0, proxy=None,
                encoding='utf-8'):
        header = self.rand_header()
        try:
            requests.Session()
            if is_proxy == 1:
                if proxy is None:
                    print('===   proxy is empty     ====')
                    return None
                res = requests.get(url, headers=header, timeout=time_out, proxies=proxy)
            else:
                res = requests.get(url, headers=header, timeout=time_out)
            res.raise_for_status()
        except requests.RequestException:
            # if tries_num > 0:
            #     time.sleep(sleep_time)
            #     print(self.get_current_time(), url, 'URL Connection Error in ', max_retry - tries_num, ' try')
            #     return self.get_url(url, tries_num - 1, sleep_time + 10, time_out + 10, max_retry, is_proxy, proxy)
            QMessageBox.warning(
                dialog_object,
                '请求错误',
                '请求失败，请检查网络连接！')
            return -1

        res.encoding = encoding  # 指定网页编码格式
        return res

    def query_words(self, word, dialog_object):
        url = 'http://dict.youdao.com/w/{}/'.format(word)
        html = self.get_url(url, dialog_object)
        if html == -1:
            return -1
        soup = BeautifulSoup(html.text, 'html.parser')
        trans_container = soup.find(class_='trans-container')
        pronunciation_container = soup.find(class_='baav')

        if not trans_container:
            ''' not found the translation '''
            return [word]

        trans_li = trans_container.find_all('li')
        trans_data = []
        if pronunciation_container and pronunciation_container.find(class_='phonetic'):
            pronounce = ""
            pronounce += pronunciation_container.text.strip()\
                .replace("\r", "")\
                .replace("\n", "")\
                .replace(" ", "")\
                .replace("[", " [")\
                .replace("]", "] ")
            # for span in pronunciation_container.find_all('span'):
            #     print(span)
            # print(pronounce)
            trans_data.append(pronounce)
        for li in trans_li:
            trans_data.append(li.text.strip())
        return trans_data
