import requests
from bs4 import BeautifulSoup
import urllib.parse
import streamlit as st
import time

def google_search(keyword, site, page=0, headers=None):
    """
    Enhanced Google search function with multiple parsing strategies
    """
    search_results = []
    
    try:
        # Construct the search query
        query = f'site:{site} "We don\'t know when or if this item will be back in stock." {keyword}'
        search_url = f'https://www.google.com/search?q={urllib.parse.quote(query)}&start={page * 10}&num=10'
        
        st.write(f"Debug - 搜索URL: {search_url}")
        
        if headers is None:
            headers = {
                'User-Agent': get_random_user_agent()
            }
        
        time.sleep(2)
        
        response = requests.get(search_url, headers=headers, timeout=10)
        st.write(f"Debug - 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Debug - Save HTML for inspection
            with open("google_response.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            
            st.write("Debug - 尝试多种搜索结果解析方式...")
            
            # 尝试多种可能的结果容器类名
            search_containers = [
                soup.find_all('div', class_='g'),  # 传统结构
                soup.find_all('div', class_='tF2Cxc'),  # 另一种常见结构
                soup.find_all('div', {'data-sokoban-container': True}),  # 新结构
                soup.find_all('div', class_='yuRUbf'),  # 链接容器
                soup.find_all('div', {'jscontroller': 'SC7lYd'})  # 另一种新结构
            ]
            
            # 遍历所有可能的容器
            for containers in search_containers:
                st.write(f"Debug - 尝试解析方式，找到 {len(containers)} 个结果")
                
                if containers:
                    for container in containers:
                        try:
                            # 尝试多种方式查找链接和标题
                            link_elem = (
                                container.find('a')
                                or container.find('a', href=True)
                                or container.find_parent('a')
                                or container.find('div', class_='yuRUbf').find('a')
                            )
                            
                            title_elem = (
                                container.find('h3')
                                or container.find('div', class_='vvjwJb')
                                or container.find('div', class_='DKV0Md')
                                or link_elem.find('h3')
                            )
                            
                            if link_elem and 'href' in link_elem.attrs:
                                link = link_elem['href']
                                
                                # 验证是否为有效的Amazon链接
                                if site in link and 'http' in link:
                                    title = title_elem.text if title_elem else 'No title'
                                    if (title, link) not in search_results:  # 避免重复
                                        search_results.append((title, link))
                                        st.write(f"Debug - 找到有效结果: {title[:30]}... | {link[:50]}...")
                            
                        except Exception as e:
                            st.write(f"Debug - 处理单个结果时出错: {str(e)}")
                            continue
                    
                    # 如果这种方式找到了结果，就不再尝试其他方式
                    if search_results:
                        break
            
            st.write(f"Debug - 最终找到 {len(search_results)} 个有效结果")
            
        return search_results
        
    except Exception as e:
        st.write(f"Debug - 发生错误: {str(e)}")
        return []