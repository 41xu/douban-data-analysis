import csv
import pandas as pd

class movie:
    def __init__(self):
        self.id = 0
        self.title = ''  # 电影名
        self.year = 0  # 年份
        self.director = []  # 多个导演什么的..
        self.writer = []  # 编剧
        self.actor = []  # 主演
        self.type = []  # 类型
        self.country = []  # 国家
        self.language = []  # 语言
        self.length = 0  # 片长
        self.score = 0.0  # 评分

    def info(self):
        print('id: {}'.format(self.id))
        print('title: {}'.format(self.title))
        print('year: {}'.format(self.year))
        print('director: {}'.format(self.director))
        print('writer: {}'.format(self.writer))
        print('actor: {}'.format(self.actor))
        print('type: {}'.format(self.type))
        print('country: {}'.format(self.country))
        print('language: {}'.format(self.language))
        print('length: {}'.format(self.length))
        print('score: {}'.format(self.score))

