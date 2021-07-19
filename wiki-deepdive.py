from bs4 import BeautifulSoup
from anytree import Node, RenderTree
from anytree.exporter import JsonExporter
import requests
import urllib
import json

wikiUrl = 'https://en.wikipedia.org'
query = '/wiki/Great_Big_Sea'
known_links = []


def get_topic(link):
    return urllib.parse.unquote(link.replace('/wiki/', ''))


def get_wiki_page(keyword, parent_branch):
    url = wikiUrl + keyword
    reqs = requests.get(url)
    soup = BeautifulSoup(reqs.text, 'html.parser')

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
                'Main_Page' not in link:
            if link not in known_links:
                known_links.append(link)
                children.append(Node(get_topic(link), parent=parent_branch, link=link))
    print('found ' + str(len(children)) + ' results for keyword : ' + get_topic(keyword))


def get_wiki_tree(query, branch):
    while 1:
        get_wiki_page(query, branch)
        for child in branch.children:
            get_wiki_tree(child.link, child)

startBranch = Node(get_topic(query))

get_wiki_tree(query, startBranch)

for pre, fill, node in RenderTree(startBranch):
    print("%s%s" % (pre, node.name))

exporter = JsonExporter(indent=2, sort_keys=True)

with open(get_topic(query) + '.json', 'w') as outfile:
    json.dump(exporter.export(startBranch), outfile)
