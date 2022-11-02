from bs4 import BeautifulSoup
import requests
import re
from neo4j import GraphDatabase
from WikiPage import WikiPage


class WikiDeepDive:
    processedPages = []

    def __init__(self, uri, user, password):
        self.databaseConnection = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.databaseConnection.close()

    def add_node(self, parentNode: WikiPage, childNode: WikiPage):
        with self.databaseConnection.session() as session:
            query = (
                "MERGE (parent:WikiPage { title: $parentTitle, query: $parentQuery, url: $parentUrl }) "
                "MERGE (child:WikiPage { title: $childTitle, query: $childQuery, url: $childUrl }) "

                "MERGE (child)-[r:DESCRIBES]->(parent) "
                "RETURN parent, child, r"
            )
            session.run(query,
                        parentTitle=parentNode.title, parentQuery=parentNode.query, parentUrl=parentNode.full_url(),
                        childTitle=childNode.title, childQuery=childNode.query, childUrl=childNode.full_url())

    def process_content(self, html):
        # parse html content
        soup = BeautifulSoup(html, "html.parser")

        div = soup.find(id="mw-content-text")

        output = []

        for x in self.getLinksUntilTag(div, div.find('h2'), "^/wiki/(?!.*:)(?!.*#).*"):
            output.append(WikiPage(x['href'], x['title']))

        return output

    def getLinksUntilTag(self, html, end, regex):
        for element in html.select('div.mw-parser-output p a, h2'):

            if element == end:
                break
            if element.name == 'a':
                if element.get('href'):
                    if re.match(regex, element['href']):
                        yield element

    def processPage(self, parent, limit):

        if parent.query not in self.processedPages:
            print("Processing " + parent.query + " with limit " + str(limit))
            reqs = requests.get(parent.full_url())
            html = reqs.text

            links = self.process_content(html)
            self.processedPages.append(parent.query)
            for link in links:
                self.add_node(parent, link)

                if (limit - 1) != 0:
                    self.processPage(link, limit - 1)


if __name__ == "__main__":
    parser = WikiDeepDive("bolt://localhost:7687", "neo4j", "test")

    query = '/wiki/Wikipedia'

    parser.processPage(WikiPage(query, ""), 10)
    parser.close()
