from selenium import webdriver
import time
import pandas as pd
import requests
from Movie import movie
from multiprocessing import Process, Queue, cpu_count, Lock
import re
import numpy as np
import random

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
    # "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv2.0.1) Gecko/20100101 Firefox/4.0.1",
}

ips=["123.156.176.88","121.226.56.92","182.84.94.12","124.152.85.168","60.184.81.136","114.234.161.49",
     "106.56.245.147","182.127.106.167","119.5.181.220","218.9.192.206","112.240.183.59","117.92.68.227",
     "180.122.113.56","218.64.147.229","111.76.67.117","117.65.33.28""61.174.159.163","114.237.42.72",
     "183.147.24.115"
]
ports=["4281","3197","4282"",3012","4208","4224","4237","2991","3979","1648","8878","5521","4289",
      "4261","1863","4251","4217","5521","4224"]

total_proxies=[]

with open('proxylist.txt','r') as reader:
    for line in reader:
        proxy=line.split('\n')[0]
        http_proxy='http://'+proxy
        https_proxy='https://'+proxy
        proxies={
            'http':http_proxy,
            'https':https_proxy,
        }
        total_proxies.append(proxies)


data=pd.read_csv('test_data.csv')

url_used_judge={data.loc[i,'URL']:0 for i in range(len(data))}


def getCookies(fileName):
    cookies = {}
    with open(fileName, 'r')as f:
        for line in f.read().split(';'):
            name, value = line.split('=', 1)
            cookies[name] = value
    return cookies


# cookies = getCookies('Cookie.txt')
# print(cookies)

def getURL():
    browser = webdriver.Chrome()
    browser.get("https://movie.douban.com/tag/#/?sort=T&range=0,10&tags=%E7%94%B5%E5%BD%B1")  # 电影=%e7%94%b5%e5%bd%b1
    time.sleep(5)
    more = browser.find_element_by_class_name("more")

    for i in range(5):  # 为缩短调试时间我们先点两次
        more.click()
        time.sleep(5)

    movies = browser.find_elements_by_class_name("item")
    # print(len(movies))
    urls = []
    for item in movies:
        urls.append(item.get_attribute('href'))

    data = pd.DataFrame(columns=["URL"], data=urls)
    data['used'] = np.zeros((len(data),), dtype=np.int)
    # print(len(data))
    # print(data)
    data.to_csv("movies.csv", index=False, sep=',')


class Spider(Process):
    def __init__(self, id, urls, lock):
        Process.__init__(self)
        self.id = id  # 当前进程id
        self.urls = urls
        self.lock = lock
        self.current_movie_id = 0  # current movie id
        self.ids = []
        self.titles = []
        self.years = []
        self.directors = []
        self.writers = []
        self.actors = []
        self.types = []
        self.countries = []
        self.languages = []
        self.lengths = []
        self.scores = []

    def run(self):
        print("Process-{} Started".format(self.id))
        while not self.urls.empty():
            url = self.urls.get()
            print("Process-{} get {}".format(self.id, url))
            i = random.randint(0, len(total_proxies) - 1)
            self.get_data(url)
            # urls_used[url]=1
            # 想来想去..原本在考虑爬短评还是影评...好像影评会更认真点写吧...
            # 虽然影评的数量比短评的要少一个数量级..但是毕竟会更正经点嘛！
            self.get_review(url)
            url_used_judge[self.current_movie_id]=1
            index=data[data['URL']=="https://movie.douban.com/subject/"+str(self.current_movie_id)+"/"].index
            data.loc[index] =[url_used_judge.keys()[index], url_used_judge[url_used_judge.keys()[index]]]
            # data.loc[data[data.URL ==
            #                str("https://movie.douban.com/subject/"+str(self.current_movie_id)+"/")].index,'used']= 1
            # data.to_csv("test_data.csv",index=False,sep=',')
            print(data.loc[index])

            time.sleep(10)

        self.write_data()
        print("Process-{} End".format(self.id))

    def write_data(self):
        filename = str(str(self.id) + ".csv")
        d = pd.DataFrame(columns=['id', 'title', 'year', 'director', 'writer', 'actor', 'type', 'country', 'language',
                                  'length', 'score'])
        for i in range(len(self.ids)):
            d.loc[i, :] = [self.ids[i], self.titles[i], self.years[i], "/".join(self.directors[i]),
                           "/".join(self.writers[i]), "/".join(self.actors[i]),
                           "/".join(self.types[i]), "/".join(self.countries[i]), "/".join(self.languages[i]),
                           self.lengths[i], self.scores[i]]
        d.to_csv(filename)

    def get_data(self, url):
        try:
            requests.get(url, headers=headers)
        except :
            print("Connection Refused. Try Again.")
            # i = random.randint(0, len(total_proxies) - 1)
            time.sleep(10)
            requests.get(url, headers=headers)


        m = movie()
        context=requests.get(url, headers=headers).text
        # movie id 从url中就可获得
        self.current_movie_id = m.id = int(url[33:-1])
        # title
        pattern = re.compile('<span property="v:itemreviewed">(.*)</span>')
        m.title = re.findall(pattern, context)
        while m.title == []:
            print("Can NOT Reach {}, Sending Request Again.".format(url))
            time.sleep(10)
            # i=random.randint(0,len(total_proxies)-1)
            r = requests.get(url, headers=headers)
            m.title = re.findall(pattern, r.text)
        m.title=m.title[0]
        # year
        pattern = re.compile('<span class="year">\((\d*)\)</span>')
        m.year = re.findall(pattern, context)[0]
        # director
        pattern = re.compile('rel="v:directedBy">([^<]*)')
        m.director = re.findall(pattern, context)
        # writer
        pattern = re.compile('<a href="/celebrity/\d*/">([^<]*)</a>')
        m.writer = re.findall(pattern, context)
        # actor
        pattern = re.compile('rel="v:starring">([^<]*)</a>')
        m.actor = re.findall(pattern, context)
        # type
        pattern = re.compile('<span property="v:genre">([^<]*)</span>')
        m.type = re.findall(pattern, context)
        # country
        pattern = re.compile('<span class="pl">制片国家/地区:</span>([^<]*)')
        m.country = re.findall(pattern, context)
        # language
        pattern = re.compile('<span class="pl">语言:</span>([^<]*)')
        m.language = re.findall(pattern, context)
        # length
        pattern = re.compile('<span property="v:runtime" content="(\d+)')
        m.length = re.findall(pattern, context)[0]
        # score
        pattern = re.compile('property="v:average">([\d\.]+)</strong>')
        m.score = re.findall(pattern, context)[0]
        self.ids.append(m.id)
        self.titles.append(m.title)
        self.years.append(m.year)
        self.directors.append(m.director)
        self.writers.append(m.writer)
        self.actors.append(m.actor)
        self.types.append(m.type)
        self.countries.append(m.country)
        self.languages.append(m.language)
        self.lengths.append(m.length)
        self.scores.append(m.score)

    def get_review(self, url):  # 爬影评中前200个打分
        # i=random.randint(0,len(total_proxies)-1)

        review_url = url + 'reviews'
        try:
            requests.get(review_url, headers=headers)
        except :
            print("Connection Refused. Try Again.")
            # i = random.randint(0, len(total_proxies) - 1)
            requests.get(review_url, headers=headers)
        context = requests.get(review_url,headers=headers).text
        pattern = re.compile('<span class="thispage" data-total-page="(\d*)">')
        total_page = re.findall(pattern, context)
        user_id = []
        user_score = []
        if total_page == []:
            review_page = 1
        else:
            review_page = int(total_page[0])
        for page in range(min(review_page, 10)):

            url = review_url + '?start=' + str(page * 20)

            # i = random.randint(0, len(total_proxies) - 1)
            try:
                requests.get(url, headers=headers)
            except :
                print("Connection Refused. Try Again.")
                # i=random.randint(0,len(total_proxies)-1)
                requests.get(url, headers=headers)

            context = requests.get(url, headers=headers).text

            pattern = re.compile('<a href="https://www.douban.com/people/(.*)/" property="v:reviewer" '
                                 'class="name">.*</a>[.\s]*<span property="v:rating" '
                                 'class="allstar(\d*) main-title-rating"')
            result = re.findall(pattern, context)

            for i in range(len(result)):
                user_id.append(result[i][0])
                user_score.append(result[i][1])

        filename = str(str(self.current_movie_id) + "review.csv")
        review = pd.DataFrame(columns=['MovieID', 'UserID', 'UserScore'])
        for i in range(len(user_id)):
            review.loc[i, :] = [self.current_movie_id, user_id[i], user_score[i]]
        review.to_csv(filename)
        # data.loc[data[data.URL == str("https://movie.douban.com/subject/"+str(self.current_movie_id)+"/")].index,'used']\
        #     = 1
        # data.to_csv("test_data.csv", index=False, sep=',')
        time.sleep(10)


if __name__ == '__main__':
    # getURL() #这个函数我们跑一次得到本地的movies.csv就好了～
    # 在服务器上运行过了所以来一次这个函数就好了～～～
    n = cpu_count()
    lock = Lock()

    urls = Queue()
    # data = pd.read_csv('test_data.csv')
    for i in range(len(data)):
        url = data.loc[i, 'URL']
        # if data.loc[i, 'used'] == 0:
        if url_used_judge[url]==0:
            urls.put(url)
    pool = []
    for i in range(n):
        p = Spider(i, urls, lock)
        p.start()
        pool.append(p)
        time.sleep(3)
    for p in pool:
        p.join()
    # data.to_csv("test_data.csv")
    print(url_used_judge)
    for i in range(len(url_used_judge)):
        data.loc[i]=[url_used_judge.keys()[i],url_used_judge[url_used_judge.keys()[i]]]
    data.to_csv("test_data.csv")
    print('END')
