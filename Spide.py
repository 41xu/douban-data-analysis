import time
from multiprocessing import Process, Queue, cpu_count, Lock
import requests
import re
import pandas as pd
from Movie import movie
import numpy as np
import random
from selenium import webdriver

ua_list = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Windows NT 6.1; rv2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
    "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
]


def get_header():
    header = random.choice(ua_list)
    header = {
        "User-Agent": header
    }
    return header


def getURL():
    browser = webdriver.Chrome()
    browser.get("https://movie.douban.com/tag/#/?sort=T&range=0,10&tags=%E7%94%B5%E5%BD%B1")
    time.sleep(5)
    more = browser.find_element_by_class_name("more")

    for i in range(50):
        more.click()
        time.sleep(5)
    movies = browser.find_elements_by_class_name("item")
    urls = []
    for item in movies:
        urls.append(item.get_attribute('href'))

    global data
    data = pd.DataFrame(columns=['URL'], data=urls)
    data['used'] = np.zeros((len(data),), dtype=np.int)
    data.to_csv("movies.csv", index=False, sep=',')


class Spider(Process):
    def __init__(self, id, urls, lock):
        Process.__init__(self)
        self.id = id
        self.urls = urls
        self.lock = lock
        self.current_movie_id = 0
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
        self.user_ids = []
        self.user_scores = []
        self.count = 0
        self.movie_data = pd.DataFrame(columns=['id', 'title', 'year', 'director', 'writer', 'actor', 'type', 'country',
                                                'language', 'length', 'score', 'user_id', 'user_score'])

    def run(self):
        print("Process-{} Started.".format(self.id))

        self.movie_data = pd.DataFrame(columns=['id', 'title', 'year', 'director', 'writer', 'actor', 'type', 'country',
                                                'language', 'length', 'score', 'user_id', 'user_score'])
        while not self.urls.empty():
            url = self.urls.get()
            print("Process-{} get {}".format(self.id, url))
            self.get_data(url)
            time.sleep(10)
            self.get_review(url)
            data.loc[data[data['URL'] == str(
                "https://movie.douban.com/subject/" + str(self.current_movie_id) + "/")].index, 'used'] = 1
            time.sleep(10)

        self.movie_data.to_csv(str(str(self.id)) + ".csv")
        print("Process-{} End.".format(self.id))

    def get_data(self, url):
        header = get_header()
        try:
            r = requests.get(url, headers=header)
        except:
            print("Connection Refused. We Ary Trying Again.")
            time.sleep(10)
            header = get_header()
            r = requests.get(url, headers=header)
        context = r.text

        m = movie()
        self.current_movie_id = m.id = int(url[33:-1])
        # title
        pattern = re.compile('<span property="v:itemreviewed">(.*)</span>')
        m.title = re.findall(pattern, context)
        while m.title == []:
            print("Can NOT Reach {}, Sending Request Again.".format(url))
            time.sleep(10)
            r = requests.get(url, headers=header)
            context = r.text
            m.title = re.findall(pattern, context)
        m.title = m.title[0]
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
        if m.id == 3734350:
            m.length = 6
        elif m.id == 6146955:
            m.length = 81
        else:
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

    def get_review(self, url):
        self.user_ids = []
        self.user_scores = []
        review_url = url + "reviews"
        header = get_header()
        try:
            if self.current_movie_id == 1768351:  # 爬评论的时候这个页面404了..?
                return
            r = requests.get(review_url, headers=header)
        except:
            print("Connection Refused. We Are Trying Again.")
            header = get_header()
            r = requests.get(review_url, headers=header)
        context = r.text

        pattern = re.compile('<span class="thispage" data-total-page="(\d*)">')
        total_page = re.findall(pattern, context)
        if total_page == []:
            review_page = 1
        else:
            review_page = int(total_page[0])
        for page in range(min(review_page, 10)):
            url = review_url + '?start=' + str(page * 20)
            try:
                requests.get(url, headers=header)
            except:
                print("Connection Refused. We Are Trying Again.")
                header = get_header()
                requests.get(url, headers=header)
            context = requests.get(url, headers=header).text

            pattern = re.compile('<a href="https://www.douban.com/people/(.*)/" property="v:reviewer" '
                                 'class="name">.*</a>[.\s]*<span property="v:rating" '
                                 'class="allstar(\d*) main-title-rating"')
            result = re.findall(pattern, context)
            for i in range(len(result)):
                self.user_ids.append(result[i][0])
                self.user_scores.append(result[i][1])
                self.movie_data.loc[self.count, :] = [self.ids[-1], self.titles[-1], self.years[-1],
                                                      "/".join(self.directors[-1]), "/".join(self.writers[-1]),
                                                      "/".join(self.actors[-1]), "/".join(self.types[-1]),
                                                      "/".join(self.countries[-1]), "/".join(self.languages[-1]),
                                                      self.lengths[-1], self.scores[-1], result[i][0], result[i][1]]
                self.count = self.count + 1

            time.sleep(20)


if __name__ == '__main__':
    # getURL()#获取URL的动作只需运行一次即可
    n = cpu_count()
    lock = Lock()

    urls = Queue()
    global data
    data = pd.read_csv("total_movies.csv")
    print(len(data))
    #这里要开始使用获得的全部电影数据的前1000部进行具体信息及用户评论爬取
    data = data[0:1000]
    for i in range(0,1000):
        url = data.loc[i, 'URL']
        if data.loc[i, 'used'] == 0:
            urls.put(url)
    pool = []
    for i in range(n):
        p = Spider(i, urls, lock)
        p.start()
        pool.append(p)
        time.sleep(10)
    for p in pool:
        p.join()
    print("END")
