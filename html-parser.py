from bs4 import BeautifulSoup
import requests
import re

def process_content(html):
    # parse html content
    soup = BeautifulSoup(html, "html.parser")

    div = soup.find(id="mw-content-text")


    output = []

    
    #print(div)

    for x in getLinksUntilTag(div, div.find('h2'), "^/wiki/(?!.*:).*"):
        output.append(x['href'])

    return output

def getLinksUntilTag(html, end, regex):
    for element in html.findAll():
        if element == end:
            break
        if element.name == 'a':
            if re.match(regex, element['href']):
                yield element


wikiUrl = 'https://en.wikipedia.org'
query = '/wiki/Linked_data'

url = wikiUrl + query
reqs = requests.get(url)
html = reqs.text

html = process_content(html)

print(html)
