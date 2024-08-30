import requests
from bs4 import BeautifulSoup
import urllib.parse

def google_search(keyword, site, page=0, headers=None):
    search_results = []
    query = f'site:{site} "We don\'t know when or if this item will be back in stock." {keyword}'
    search_url = f'https://www.google.com/search?q={urllib.parse.quote(query)}&start={page * 10}'
    
    if headers is None:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    for g in soup.find_all('div', class_='g'):
        anchors = g.find_all('a')
        if anchors:
            link = anchors[0]['href']
            title = g.find('h3').text if g.find('h3') else 'No title'
            search_results.append((title, link))

    return search_results

def bing_search(keyword, site, page=0, headers=None):
    search_results = []
    query = f'site:{site} "We don\'t know when or if this item will be back in stock." {keyword}'
    search_url = f'https://www.bing.com/search?q={urllib.parse.quote(query)}&first={page * 10 + 1}'
    
    if headers is None:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    for li in soup.find_all('li', class_='b_algo'):
        h2 = li.find('h2')
        if h2:
            a = h2.find('a')
            if a:
                title = a.text
                link = a['href']
                search_results.append((title, link))

    return search_results
