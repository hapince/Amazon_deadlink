import streamlit as st
import pandas as pd
from io import BytesIO
import time
import random
from utils import google_search, bing_search

# List of user agents to randomize the header for each request
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.54',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0'
]

def get_random_user_agent():
    """Return a random User-Agent from the list."""
    return random.choice(USER_AGENTS)

def extract_asin(url):
    """Extract ASIN from Amazon product URL."""
    if "dp/" in url:
        parts = url.split("dp/")
        if len(parts) > 1:
            asin_part = parts[1].split('/')[0][:10]  # Extract only the first 10 characters
            return asin_part
    return None

def fetch_all_results(search_engine, keyword, amazon_site, max_links=50):
    """Fetch results until the desired number of links is reached."""
    page = 0
    all_results = []
    
    progress_bar = st.progress(0)  # Initialize progress bar

    while len(all_results) < max_links:
        # Set a random delay to mimic human behavior
        delay = random.uniform(2, 5)
        time.sleep(delay)
        
        if search_engine == "Google":
            headers = {'User-Agent': get_random_user_agent()}
            results = google_search(keyword, amazon_site, page, headers=headers)
        elif search_engine == "Bing":
            headers = {'User-Agent': get_random_user_agent()}
            results = bing_search(keyword, amazon_site, page, headers=headers)
        
        # If no more results are found, break the loop
        if not results:
            break

        all_results.extend(results)
        
        # If more results than needed, truncate the list
        if len(all_results) > max_links:
            all_results = all_results[:max_links]
        
        # Update progress bar
        progress = len(all_results) / max_links
        progress_bar.progress(progress)
        
        page += 1

    progress_bar.progress(1.0)  # Ensure the progress bar reaches 100%
    
    return all_results

def main():
    st.title("亚马逊僵尸链接查询工具")
    st.write("遇到问题联系：happy_pzzzzz")
    st.subheader("搜索设置")
    search_engine = st.selectbox("选择搜索引擎", ["Google", "Bing"])
    amazon_site = st.selectbox("选择亚马逊站点", [
        "amazon.com", "amazon.ca", "amazon.co.uk", "www.amazon.com.au", 
        "www.amazon.in", "www.amazon.sg", "www.amazon.ae"
    ])
    keyword = st.text_input("输入关键词")
    max_links = st.slider("查询链接数限制", 10, 200, 50)  # Allow user to set maximum number of links to fetch

    if st.button("搜索"):
        # Fetch results from all pages
        all_results = fetch_all_results(search_engine, keyword, amazon_site, max_links)

        if all_results:
            # Filter out links containing 'sellercentral'
            filtered_results = [
                (title, link) for title, link in all_results 
                if "sellercentral" not in link
            ]

            if filtered_results:
                # Store filtered results in session state
                st.session_state.results = []
                for title, link in filtered_results:
                    asin = extract_asin(link)
                    st.session_state.results.append({"Title": title, "URL": link, "ASIN": asin})

                st.subheader(f"搜索结果-试用版限制{len(filtered_results)}条 ({search_engine})")
                for i, result in enumerate(st.session_state.results, start=1):
                    st.markdown(f"**{i}. [{result['Title']}]({result['URL']})**")
                
                # Prepare DataFrame for download
                df = pd.DataFrame(st.session_state.results)
                excel_buffer = BytesIO()
                df.to_excel(excel_buffer, index=False, engine='openpyxl')
                excel_buffer.seek(0)

                # Download button for the Excel file
                st.download_button(
                    label="导出并下载Excel",
                    data=excel_buffer,
                    file_name="search_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.write("未找到相关结果（已排除包含'sellercentral'的链接）")
        else:
            st.write("未找到相关结果")

    st.subheader("联系方式")
    st.write("关注公众号“Hapince出海日记”")
    st.write("或添加客服微信：happy_prince45")

def check_password():
    """Returns `True` if the user enters the correct password."""
    if "password_correct" not in st.session_state:
        st.subheader("用户认证")
        password = st.text_input("请输入密码", type="password")
        if st.button("提交"):
            if password == "happyprince":  # Set password to 'happyprince'
                st.session_state.password_correct = True
            else:
                st.error("密码错误，请重试")
                st.session_state.password_correct = False

    return st.session_state.get("password_correct", False)

if __name__ == "__main__":
    if check_password():
        main()
    else:
        st.warning("由于服务器资源有限，为避免不必要流量，请进入官方群或关注微信公众号“Hapince出海日记”获取密码")
        st.image("image/wechatgroup.jpg")
