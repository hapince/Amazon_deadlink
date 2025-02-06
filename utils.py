# 在 utils.py 中修改 google_search 函数
def google_search(keyword, site, page=0, headers=None):
    """
    Enhanced Google search function with detailed debugging output
    """
    search_results = []
    
    # Construct the search query
    query = f'site:{site} "We don\'t know when or if this item will be back in stock." {keyword}'
    search_url = f'https://www.google.com/search?q={urllib.parse.quote(query)}&start={page * 10}'
    
    # Debug output
    st.write(f"Debug - 搜索URL: {search_url}")
    
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    try:
        st.write("Debug - 发送请求...")
        response = requests.get(search_url, headers=headers, timeout=10)
        st.write(f"Debug - 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Debug - 保存响应内容到文件
            with open("response_debug.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            
            st.write("Debug - 开始解析搜索结果...")
            
            # 尝试不同的Google搜索结果类名
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
            
            st.write(f"Debug - 总共找到 {len(search_results)} 个有效结果")
        else:
            st.write(f"Debug - 请求失败，状态码: {response.status_code}")
            
        return search_results
        
    except Exception as e:
        st.write(f"Debug - 发生错误: {str(e)}")
        return []

# 在主程序中修改 fetch_all_results 函数
def fetch_all_results(keyword, amazon_site, max_links=50):
    """Fetch results with enhanced debugging"""
    page = 0
    all_results = []
    
    st.write("=== 开始搜索调试信息 ===")
    st.write(f"关键词: {keyword}")
    st.write(f"目标站点: {amazon_site}")
    st.write(f"请求数量: {max_links}")
    
    progress_bar = st.progress(0)
    
    while len(all_results) < max_links and page < 3:  # 限制最大页数为3
        st.write(f"\n--- 正在处理第 {page + 1} 页 ---")
        
        # 添加延迟
        delay = random.uniform(2, 4)
        st.write(f"等待 {delay:.1f} 秒...")
        time.sleep(delay)
        
        headers = {'User-Agent': get_random_user_agent()}
        st.write(f"使用 User-Agent: {headers['User-Agent']}")
        
        try:
            results = google_search(keyword, amazon_site, page, headers=headers)
            
            if results:
                st.write(f"本页找到 {len(results)} 个结果")
                all_results.extend(results)
                
                if len(all_results) >= max_links:
                    all_results = all_results[:max_links]
                    break
            else:
                st.write("本页未找到结果")
                break
                
            progress = min(len(all_results) / max_links, 1.0)
            progress_bar.progress(progress)
            
            page += 1
            
        except Exception as e:
            st.write(f"处理页面时发生错误: {str(e)}")
            break
    
    progress_bar.progress(1.0)
    st.write(f"\n=== 搜索完成 ===")
    st.write(f"总共找到: {len(all_results)} 个结果")
    
    return all_results