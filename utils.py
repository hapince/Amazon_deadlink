def fetch_all_results(keyword, amazon_site, max_links=50):
    """Fetch results until the desired number of links is reached."""
    page = 0
    all_results = []
    
    st.write("=== 开始搜索 ===")
    st.write(f"关键词: {keyword}")
    st.write(f"目标站点: {amazon_site}")
    
    progress_bar = st.progress(0)
    
    # Validate inputs
    if not keyword or not amazon_site:
        st.error("关键词和站点不能为空")
        return []
        
    try:
        while len(all_results) < max_links and page < 3:  # 限制最大页数为3
            st.write(f"\n--- 正在搜索第 {page + 1} 页 ---")
            
            # Random delay between requests
            delay = random.uniform(2, 4)
            time.sleep(delay)
            
            # Rotate user agents
            headers = {'User-Agent': get_random_user_agent()}
            
            results = google_search(keyword, amazon_site, page, headers=headers)
            
            if results:
                st.write(f"本页找到 {len(results)} 个结果")
                all_results.extend(results)
                
                if len(all_results) >= max_links:
                    all_results = all_results[:max_links]
                    break
            else:
                st.write("本页未找到结果")
                # Don't break immediately, try next page
                if page >= 2:  # If we've tried 3 pages with no results, then stop
                    break
            
            progress = min(len(all_results) / max_links, 1.0)
            progress_bar.progress(progress)
            
            page += 1
            
    except Exception as e:
        st.error(f"搜索过程中发生错误: {str(e)}")
    
    progress_bar.progress(1.0)
    st.write(f"\n=== 搜索完成 ===")
    st.write(f"总共找到: {len(all_results)} 个结果")
    
    return all_results