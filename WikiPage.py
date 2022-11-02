class WikiPage:
    wikiUrl = 'https://en.wikipedia.org'

    def __init__(self, query, title):
        self.query = query
        self.title = title

    def full_url(self):
        return self.wikiUrl + self.query
