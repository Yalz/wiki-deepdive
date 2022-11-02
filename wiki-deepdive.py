from bs4 import BeautifulSoup
import requests
import re
from neo4j import GraphDatabase

class WikiDeepDive:
    processedPages = []

    def __init__(self, uri, user, password):
        self.databaseConnection = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.databaseConnection.close()

    def add_node(self, topic, link):
        with self.databaseConnection.session() as session:
            query = (
                "MERGE (parent:WikiPage { topic: $topic }) "
                "MERGE (child:WikiPage { topic: $link }) "

                "MERGE (parent)-[r:LINK]->(child) "
                "RETURN parent, child, r"
            )
            session.run(query, topic=topic, link=link)

    def process_content(self, html):
        # parse html content
        soup = BeautifulSoup(html, "html.parser")

        div = soup.find(id="mw-content-text")

        output = []

        for x in self.getLinksUntilTag(div, div.find('h2'), "^/wiki/(?!.*:)(?!.*#).*"):
            output.append(x['href'])

        return output

    def getLinksUntilTag(self, html, end, regex):
        for element in html.findAll(['a','h2']):
            if element == end:
                break
            if element.name == 'a':
                if element.get('href'): 
                    if re.match(regex, element['href']):
                        yield element

    def processPage(self, query, limit):
        root = wikiUrl + query

        if (root not in self.processedPages):
            print("Processing " + query + " with limit " + str(limit))
            url = wikiUrl + query
            reqs = requests.get(url)
            html = reqs.text

            links = self.process_content(html)
            self.processedPages.append(root)
            for link in links :
                linkRef = wikiUrl + link

                self.add_node(root, linkRef)

                if ((limit - 1) != 0):
                    self.processPage(link, limit - 1)

if __name__ == "__main__":
    parser = WikiDeepDive("bolt://localhost:7687", "neo4j", "test")

    wikiUrl = 'https://en.wikipedia.org'
    query = '/wiki/Wikipedia'

    parser.processPage(query, 2)
    parser.close()
