import urllib
from subprocess import check_output

import requests
import yaml
from anytree import Node, RenderTree
from anytree.exporter import DictExporter, DotExporter
from bs4 import BeautifulSoup

wikiUrl = 'https://en.wikipedia.org'
query = '/wiki/Adelina_(given_name)'
known_links = []


def get_topic(link):
    data = urllib.parse.unquote(link.replace('/wiki/', ''))
    return data.encode().decode()


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


def get_wiki_page(keyword, parent_branch):
    url = wikiUrl + keyword
    reqs = requests.get(url)

    soup = process_content(reqs.text)

    children = []
    for linkTag in soup.find_all('a'):
        link = linkTag.get('href')
        if link is not None and link.startswith('/wiki') and \
                'File:' not in link and \
                'Category:' not in link and \
                'Help:' not in link and \
                'Wikipedia:' not in link and \
                'Special:' not in link and \
                'Portal:' not in link and \
                'User:' not in link and \
                'Template:' not in link and \
                'Talk:' not in link and \
                'Main_Page' not in link and \
                'Wikipedia_talk:' not in link and \
                'MOS:' not in link:
            if link not in known_links:
                known_links.append(link)
                children.append(Node(get_topic(link), parent=parent_branch, link=link))
    print('found ' + str(len(children)) + ' results for keyword : ' + get_topic(keyword))


def get_wiki_tree(query, branch):
    # L1
    get_wiki_page(query, branch)

    print('--- parent done ---')

    for child in branch.children:
        get_wiki_page(child.link, child)

        print('done with child: ' + child.name)


def get_export_filename(query, type):
    return get_topic(query) + '.' + type


startBranch = Node(get_topic(query))

get_wiki_tree(query, startBranch)

for pre, fill, node in RenderTree(startBranch):
    print("%s%s" % (pre, node.name))

with open(get_export_filename(query, 'yaml'), "w+") as file:  # doctest: +SKIP
    yaml.dump(DictExporter().export(startBranch), file)

DotExporter(startBranch).to_dotfile(get_export_filename(query, 'dot'))

check_output("dot " + get_export_filename(query, 'dot') + " -T svg -o " + get_export_filename(query, 'svg'),
             shell=True).decode()
