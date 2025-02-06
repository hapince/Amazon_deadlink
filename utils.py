import requests
from bs4 import BeautifulSoup
import urllib.parse

def google_search(keyword, site, page=0, headers=None):
    """
    Perform a Google search for Amazon products that are out of stock.
    
    Args:
        keyword (str): Search keyword
        site (str): Amazon site to search (e.g., amazon.com)
        page (int): Page number for pagination
        headers (dict): HTTP headers for the request
        
    Returns:
        list: List of tuples containing (title, link) pairs
    """
    search_results = []
    
    # Construct the search query
    query = f'site:{site} "We don\'t know when or if this item will be back in stock." {keyword}'
    search_url = f'https://www.google.com/search?q={urllib.parse.quote(query)}&start={page * 10}'
    
    # Set default headers if none provided
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    try:
        # Add timeout to prevent hanging
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an error for bad status codes
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for search results with class 'g'
        for g in soup.find_all('div', class_='g'):
            try:
                anchors = g.find_all('a')
                if anchors:
                    link = anchors[0]['href']
                    # Only include Amazon links
                    if site in link:
                        title = g.find('h3').text if g.find('h3') else 'No title'
                        search_results.append((title, link))
            except Exception as e:
                print(f"Error processing search result: {e}")
                continue
        
        return search_results
        
    except requests.exceptions.RequestException as e:
        print(f"Error during Google search: {e}")
        return []