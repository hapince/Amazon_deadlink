import requests
from bs4 import BeautifulSoup
import urllib.parse
import streamlit as st
import time

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
    
    try:
        # Construct the search query
        query = f'site:{site} "We don\'t know when or if this item will be back in stock." {keyword}'
        search_url = f'https://www.google.com/search?q={urllib.parse.quote(query)}&start={page * 10}'
        
        st.write(f"Debug - 搜索URL: {search_url}")
        
        # Set default headers if none provided
        if headers is None:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        
        # Add a small delay before making the request
        time.sleep(2)
        
        response = requests.get(search_url, headers=headers, timeout=10)
        st.write(f"Debug - 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try different Google search result class names
            search_divs = soup.find_all('div', class_='g')
            if not search_divs:
                search_divs = soup.find_all('div', class_='tF2Cxc')
            
            st.write(f"Debug - 找到 {len(search_divs)} 个搜索结果div")
            
            for g in search_divs:
                try:
                    anchors = g.find_all('a')
                    if anchors:
                        link = anchors[0]['href']
                        if site in link:
                            title = g.find('h3')
                            title_text = title.text if title else 'No title'
                            search_results.append((title_text, link))
                            st.write(f"Debug - 找到有效结果: {title_text[:30]}...")
                except Exception as e:
                    st.write(f"Debug - 处理单个结果时出错: {str(e)}")
                    continue
        
        return search_results
        
    except Exception as e:
        st.write(f"Debug - 发生错误: {str(e)}")
        return []