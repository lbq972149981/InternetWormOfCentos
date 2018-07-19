#coding:utf-8
from bs4 import BeautifulSoup
import threading
import multiprocessing
import time
import sys
import re
import os
import requests
from urllib.request import *
import datetime
# makedir
def mkdir(path):
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)
# download
def download(url,FilePath):
    response = requests.get(url, stream=True)
    status = response.status_code
    if status == 200:
        with open(FilePath, "wb") as fp:
            fp.write(response.content)
# Hander
def Handler(start, end, url, Filepath):
    headers = {'Range': 'bytes=%d-%d' % (start, end)}
    response = requests.get(url, headers=headers, stream=True)
    status = response.status_code
    if status == 200:
        with open(Filepath, "r+b") as fp:
            fp.seek(start)
            var = fp.tell()
            fp.write(response.content)
# Threading_download
def Threading_download(url,filePath,num_thread):
    t1 = datetime.datetime.now().replace(microsecond=0)
    response = requests.head(url)
    Filepath = filePath
    file_size = (int)(response.headers['content-length'])
    fp = open(Filepath, "wb")
    fp.truncate(file_size)
    fp.close()
    part = file_size // num_thread
    for i in range(num_thread):
        start = part*i
        if i == num_thread-1:
            end = file_size
        else:
            end = start + part
        t = threading.Thread(target=Handler, kwargs={'start': start, 'end': end, 'url': url, 'Filepath': Filepath})
        t.setDaemon(True)
        t.start()
    main_thread = threading.current_thread()
    for t in threading.enumerate():
        if t is main_thread:
            continue
        t.join()
    t2 = datetime.datetime.now().replace(microsecond=0)
    time = t2 - t1
    filename = Filepath.split('/')[-1]
    res = filename + "下载完成----用时:" + str(time)
    # print(res)
# openPage
def openPage(pageUrl) :
    web = urlopen(pageUrl)
    html = web.read()
    soup = BeautifulSoup(html,'html.parser')
    links = soup.find_all('a')
    return links

# url file
def getUrlsOrFiles(links):
    urls = list()
    files = list()
    for link in links[1:]:
        newlink = link['href']
        if newlink.endswith("/"):
            urls.append(newlink)
        else:
            files.append(newlink)
    return urls,files

# doWrite
def doWrite(url,path):
    links = openPage(url)
    urls, files = getUrlsOrFiles(links)
    fileSizes = getFileSizes(url,files)
    if files:
        for file in files:
            # print(file + "-----" + path + file + ".txt")
            # f = open(path + file + ".txt", "w")
            # Threading_download(url+file,path+file,5)
            if os.path.exists(path+file):
                filesize = os.path.getsize(path+file)
                if fileSizes[url+file]!=filesize:
                    download(url + file, path + file)
            else:
                download(url + file, path + file)
    if urls:
        for v in urls:
            dirName = v[:-1]
            newpath = path+dirName+"/"
            if os.path.exists(newpath)==False:
                mkdir(newpath)
            doWrite(url + v, newpath)
def runWork():
   while 1:
       doWrite('https://mirrors.aliyun.com/centos/', "D:/www/")
       time.sleep(3600*24)
def getFileSizes(url,files):
    web = urlopen(url)
    html = web.read()
    soup = BeautifulSoup(html, 'html.parser')
    filesize = soup.find_all('pre')[0]
    filesize = str(filesize)
    fs = []
    fileSizes ={}
    with open("fileSize", "w") as ff:
        ff.write(filesize)
    with open("fileSize", "r") as ff:
        lines = ff.readlines()
        for v in lines:
            if v != '\n':
                num = re.findall("\d+", v)
                if len(num) > 4:
                    fs.append(num[-1])
    for i in range(len(files)):
        fileSizes[url+files[i]] = fs[i]
    return fileSizes
if __name__ == '__main__':
    p = multiprocessing.Process(target=runWork,)
    p.start()

