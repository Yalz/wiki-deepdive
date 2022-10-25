from bs4 import BeautifulSoup
import requests


def process_content(html):
    # parse html content
    soup = BeautifulSoup(html, "html.parser")

    div = soup.find(id="mw-content-text")
    div = next(div.children, None)

    output = BeautifulSoup("", "html.parser")
    for x in between(div, div.find('p'), div.find('h2')):
        output.append(x)

    return output


def between(html, start, end):
    found_first_element = False

    for element in html.findAll(['p', 'h2']):
        if element == end:
            break
        if element == start:
            found_first_element = True
        if found_first_element:
            yield element


wikiUrl = 'https://en.wikipedia.org'
query = '/wiki/Abdullah_II_of_Jordan'

url = wikiUrl + query
reqs = requests.get(url)
html = reqs.text

html = process_content(html)

print(html)
