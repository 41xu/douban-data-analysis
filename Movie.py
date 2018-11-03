class movie:

    def __init__(self):
        self.id = id
        self.title = ''
        self.year = 0
        self.director = []
        self.writer = []
        self.actor = []
        self.type = []
        self.country = []
        self.language = []
        self.length = 0
        self.score = 0.0

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
