# -*- coding: utf-8 -*-
# 总体程序
import requests, time, csv
from bs4 import BeautifulSoup
import threading  # 线程
import queue  # 队列
import re

# ipqueue=queue.Queue()  #ip池队列
# tagsqueue=queue.Queue() #标签队列
# idqueue=queue.Queue()  #id队列
# resultsqueue=queue.Queue() #结果队列 存放爬取到的书籍的id，书名，国家，作者，评分，摘要，热门标签
idlist = []  # id数组，记录所有书籍id 用于爬取时查重


class Proxies():  # ip类，从代理网站取ip，在检查可用性后将可用ip加入队列供使用
    def __init__(self):
        self.headers = {
            'Connection': 'Keep-Alive',
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'Mozilla/6.1 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'
        }
        self.ip_list = []
        self.ipqueue = queue.Queue()

    def get_ip_list(self):  # 从代理网站获取代理ip
        print("正在获取代理列表...")
        url = 'http://www.xicidaili.com/nn/'
        for i in range(1, 4):
            html = requests.get(url=url + str(i), headers=self.headers).text
            soup = BeautifulSoup(html, 'lxml')
            ips = soup.find(id='ip_list').find_all('tr')
            for i in range(1, len(ips)):
                ip_info = ips[i]
                tds = ip_info.find_all('td')
                self.ip_list.append(tds[1].text + ':' + tds[2].text)
        print("代理列表抓取成功.")
        # print(self.ip_list)
        return self.ip_list

    def check_ip(self):  # 检查ip可用性,保留可用ip
        for ip in self.ip_list:
            proxies = {'http': 'http://' + ip, 'https': 'http://' + ip}
            # print(proxies)
            try:
                print('checking ip %s ' % ip)
                s = requests.get('https://book.douban.com/subject/30180673/', headers=self.headers, proxies=proxies)
                # print(s.text)
                if str(s) == '<Response [403]>':
                    print('%s cannot be used' % ip)
                    self.ip_list.remove(ip)
            except:
                print('%s cannot be used' % ip)
                self.ip_list.remove(ip)
        for ip in ip_list:  # 入队
            self.ipqueue.put(ip)


def tagsCrawler():  # 标签爬虫，获取所有标签
    def __init__(self):
        self.url = 'https://book.douban.com/tag/?view=type&icn=index-sorttags-all'
        self.tagsqueue = queue.Queue()

    def getTags(self):
        content = requests.get(self.url)
        soup = BeautifulSoup(content.text, 'lxml')
        tables = soup.find_all('table', class_='tagCol')
        for table in tables:
            tags = table.find_all('td')
            tags = map(lambda x: x.a.text, tags)
            for tag in tags:
                self.tagsqueue.put(tag.strip())
        return self.tagsqueue


# 书籍id爬虫线程,提取书签队列信息分别抓取书籍id号
class booknameThread(threading.Thread):
    def __init__(self, tagsqueue, idqueue, ipqueue):
        threading.Thread.__init__(self)
        self.headers = {
            'Connection': 'Keep-Alive',
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'Mozilla/6.1 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'
        }
        self.ip = ''
        self.tagsqueue = tagsqueue
        self.idquque = idqueue
        self.ipqueue = ipqueue

    def getIDs(self):  # 遍历每个标签，获取所有书籍的id
        count = 0
        while self.tagsqueue.empty() != True:
            try:
                if count == 0:  # 获取ip或者重置ip
                    self.ip = self.ipqueue.get()
                    proxies = {'http': 'http://' + self.ip, 'https': 'https//' + self.ip}
                if count % 3 == 2:
                    self.ipququ.put(self.ip)
                    self.ip = self.ipqueue.get()
                    proxies = {'http': 'http://' + self.ip, 'https': 'https//' + self.ip}
                tag = self.tagsqueue.get()
                print('crawlerThread getting id %s' % tag)
                for i in range(0, 100):
                    url2 = 'https://book.douban.com/tag/' + tag + '?start=' + str(i * 20) + '&type=T'
                    content2 = requests.get(url2, headers=self.headers, proxies=proxies)
                    soup2 = BeautifulSoup(content2.text, 'lxml')
                    books = soup2.find_all('div', class_='info')
                    herfs = map(lambda x: x.h2.a['href'], books)
                    herfs = list(herfs)  # 解析所有网页书籍链接
                    if herfs:
                        for herf in herfs:
                            herf = re.sub(r'https://book.douban.com/subject/', '', herf)
                            herf = re.sub(r'/', '', herf)  # 分解出书籍id
                            # print(herf)
                            self.idqueue.put(herf)  # id入队
                    else:  # 直到页面没有新书跳出循环
                        print('crawlerThread finish id %s' % tag)
                        break  # 查询完标签所有书籍后自动跳出循环
            except:
                self.ipququ.put(self.ip)
                self.ip = self.ipqueue.get()
                proxies = {'http': 'http://' + self.ip, 'https': 'https//' + self.ip}
                pass
                # print(idlist)

    def run(self):
        # self.getTags()
        self.getIDs()


# 书籍具体信息爬虫线程,提取id队列信息分别抓取书籍具体信息，并写入文件夹
class getInfoThread(threading.Thread):
    def __init__(self, idqueue, ipqueue, outfile):
        threading.Thread.__init__(self)
        self.headers = {
            'Connection': 'Keep-Alive',
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'Mozilla/6.1 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'
        }
        self.ip = ''
        self.idquque = idqueue
        self.ipqueue = ipqueue
        self.outfile = outfile


    def getInfos(self):  # 遍历书籍id,请求url获取网页书籍
        with open(self.outfile, 'a+', encoding='utf-8', newline='') as csvwrite:
            w = csv.write(csvwrite)
            self.ip = self.ipqueue.get()  # ip初始化
            proxies = {'http': 'http://' + self.ip, 'https': 'https//' + self.ip}
            count = 0
            while self.idqueue.empty() != True:
                try:
                    num = self.idqueue.get()
                    if count % 200 == 199:
                        self.ipququ.put(self.ip)
                        self.ip = self.ipqueue.get()
                        proxies = {'http': 'http://' + self.ip, 'https': 'https//' + self.ip}
                    url = 'https://book.douban.com/subject/' + num + '/'
                    bookinfo = []
                    bookinfo.append(num)
                    content3 = requests.get(url, headers=self.headers, proxies=self.proxies)
                    soup3 = BeautifulSoup(content3.text, 'lxml')
                    title = soup3.find('span', attrs={'property': 'v:itemreviewed'}).text  # 解析标题
                    bookinfo.append(title)
                    infos = soup3.find('div', id='info').a.text  # 解析国籍和作者
                    infos = re.sub('\n', '', infos).strip()
                    if re.search(r'\[.*\]', infos):
                        infos = infos.split(' ')
                        nation = infos[0].strip()
                        author = infos[-1].strip()
                    else:
                        nation = '[中]'
                        author = infos.strip()
                    bookinfo.append(nation)
                    bookinfo.append(author)
                    grade = soup3.find('strong', attrs={'property': 'v:average'}).text  # 解析评分
                    bookinfo.append(grade)
                    abstract = soup3.find('div', class_='intro').text  # 解析摘要
                    abstract = re.sub('\n', '', abstract)
                    bookinfo.append(abstract)
                    tags = soup3.find_all('a', class_='tag')  # 解析标签
                    tags = map(lambda x: x.text, tags)
                    tags = list(tags)
                    bookinfo.append(tags)
                    w.writerow(bookinfo)
                except:
                    self.ipququ.put(self.ip)
                    self.ip = self.ipqueue.get()
                    proxies = {'http': 'http://' + self.ip, 'https': 'https//' + self.ip}
                    pass

    def run(self):
        self.getInfos()


if __name__ == '__main__':
    outfile = r'F:\data\douban\info.csv'
    ip = Proxies()
    ip.get_ip_list()
    ipqueue = ip.check_ip()
    tc = tagsCrawler()
    tagsqueue = tc.getTags()
    idqueue = queue.Queue()
    thread1 = booknameThread(tagsqueue, idqueue, ipqueue)
    thread2 = getInfoThread(idqueue, ipqueue, outfile)
    # thread2=urlsThread(tagsqueue,urlsqueue)
    thread1.start()
    time.sleep(5)
    thread2.start()
    thread1.join()
    thread2.join()
    print('返回主线程')