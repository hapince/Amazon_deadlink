import streamlit as st
import pandas as pd
from io import BytesIO
import time
import random
import requests
from bs4 import BeautifulSoup
import os
import json

# List of user agents to randomize the header for each request
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/92.0.902.62',
    'Mozilla/5.0 (Linux; Android 11; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Mobile Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15'
]

# Path to the file storing user count
USER_COUNT_FILE = "user_count.txt"

class GoogleCustomSearch:
    def __init__(self):
        """使用固定API Key和搜索引擎ID"""
        self.api_key = "AIzaSyBZW3AwzoW4d83NinvUKu78HD0MnE7Ccbg"
        self.cx = "0670ded1136164adf"
        self.base_url = "https://www.googleapis.com/customsearch/v1"
    
    def search(self, query, site=None, start_index=1, num=10):
        """
        使用Google Custom Search API进行搜索
        
        Args:
            query (str): 搜索关键词
            site (str): 限制搜索的网站 (例如 "amazon.com")
            start_index (int): 结果起始索引 (1-based)
            num (int): 每页结果数量 (最大值为10)
            
        Returns:
            list: 结果列表，每个结果为(标题, 链接)对
        """
        # 如果提供了网站，将其添加到查询中
        full_query = query
        if site:
            full_query = f"{query} 'We don\'t know when or if this item will be back in stock.' site:{site}"
        
        params = {
            'key': self.api_key,
            'cx': self.cx,
            'q': full_query,
            'start': start_index,
            'num': num
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            if response.status_code != 200:
                st.error(f"API请求失败: {response.status_code} - {response.text}")
                return []
            
            data = response.json()
            
            # 检查是否有搜索结果
            if 'items' not in data:
                return []
                
            results = []
            for item in data['items']:
                title = item.get('title', '')
                link = item.get('link', '')
                results.append((title, link))
                
            return results
            
        except Exception as e:
            st.error(f"搜索过程中发生错误: {str(e)}")
            return []

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

def extract_image_url(asin):
    """Extract the main image URL from the Amazon product page."""
    headers = {'User-Agent': get_random_user_agent()}
    product_url = f"https://www.amazon.com/dp/{asin}"
    response = requests.get(product_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the image URL using different strategies
    img_tag = soup.find('img', {'id': 'landingImage'})  # Main product image
    if not img_tag:
        img_tag = soup.find('img', {'class': 'a-dynamic-image'})  # Another common class for images
    
    if img_tag and 'src' in img_tag.attrs:
        return img_tag['src']
    
    return None

def fetch_all_results(keyword, amazon_site, max_links=50):
    """Fetch results until the desired number of links is reached using Google Custom Search API."""
    page = 0
    all_results = []
    st.write(f"关键词: {keyword} 目标站点: {amazon_site}")
    
    progress_bar = st.progress(0)
    
    # 实例化Google Custom Search类
    google_search = GoogleCustomSearch()
    
    # Validate inputs
    if not keyword or not amazon_site:
        st.error("关键词和站点不能为空")
        return []
        
    try:
        while len(all_results) < max_links and page < 10:  # 限制最大页数为10
            start_index = page * 10 + 1
            
            # Random delay between requests
            delay = random.uniform(2, 4)
            time.sleep(delay)
            
            # 执行搜索
            results = google_search.search(keyword, amazon_site, start_index, num=10)
            
            if results:
                all_results.extend(results)
                if len(all_results) >= max_links:
                    all_results = all_results[:max_links]
                    break
            else:
                if page >= 2:  # If we've tried 3 pages with no results, then stop
                    break
            
            progress = min(len(all_results) / max_links, 1.0)
            progress_bar.progress(progress)
            
            page += 1
            
    except Exception as e:
        st.error(f"搜索过程中发生错误: {str(e)}")
    
    progress_bar.progress(1.0)
    st.write(f"\n=== 采集完毕 ===")
    
    return all_results

def update_user_count(increment=1):
    """
    Update and return the current user count by a specified increment.
    
    Args:
        increment (int): The value to increase or decrease the user count by.
                         Default is 1 (increase by 1).
    
    Returns:
        int: The updated user count.
    """
    if not os.path.exists(USER_COUNT_FILE):
        with open(USER_COUNT_FILE, "w") as f:
            f.write("1000")
    
    with open(USER_COUNT_FILE, "r") as f:
        user_count = int(f.read().strip())
    
    user_count += increment
    
    with open(USER_COUNT_FILE, "w") as f:
        f.write(str(user_count))
    
    return user_count

def display_user_count(user_count):
    """Display the user count at the bottom left corner without overlapping."""
    st.markdown(
        f"""
        <div style='
            position: fixed;
            bottom: 10px;
            left: 10px;
            background-color: white;
            padding: 5px 10px;
            border-radius: 5px;
            box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
            z-index: 1000;
            font-weight: bold;
            color: #333;
            font-size: 14px;'>
            使用人数: {user_count}
        </div>
        """,
        unsafe_allow_html=True
    )

def main():
    st.title("亚马逊僵尸链接采集工具")
    st.write("建议给主要关键词加上英文双引号，以提高搜索结果精确性。")
    
    # 创建亚马逊站点的映射
    amazon_sites = {
        "amazon.com": "美国站",
        "amazon.ca": "加拿大站",
        "amazon.co.uk": "英国站",
        "www.amazon.com.au": "澳大利亚站",
        "www.amazon.in": "印度站",
        "www.amazon.sg": "新加坡站",
        "www.amazon.ae": "阿联酋站"
    }

    # 将输入部分放入侧边栏
    with st.sidebar:
        st.title("僵尸链接采集工具：")
        st.write("")
        selected_site = st.selectbox("选择亚马逊站点", list(amazon_sites.values()))
        # 获取对应的英文站点
        amazon_site = list(amazon_sites.keys())[list(amazon_sites.values()).index(selected_site)]

        keyword = st.text_input("输入关键词")
        max_links = st.slider("查询链接条数", 1, 100, 10)

        # 搜索按钮放在侧边栏
        search_button = st.button("搜索")
        st.subheader("联系方式")
        st.write("遇到问题请添加微信：hapince")
        st.write("关注公众号\"Hapince出海日记\"")
        st.image("image/publicwechat.jpg")

    # 当用户点击搜索按钮时执行搜索
    if search_button:
        all_results = fetch_all_results(keyword, amazon_site, max_links)

        if all_results:
            filtered_results = [
                (title, link) for title, link in all_results 
                if "sellercentral" not in link
            ]

            if filtered_results:
                st.session_state.results = []
                for title, link in filtered_results:
                    asin = extract_asin(link)
                    image_url = extract_image_url(asin) if asin else None
                    image_tag = f'<img src="{image_url}" style="width:100px;height:100px;object-fit:cover;"/>' if image_url else f'<img src="https://kaspabuy.shop/wp-content/uploads/2024/10/pdt.jpg" style="width:100px;height:100px;object-fit:cover;"/>'
                    st.session_state.results.append({"Image": image_tag, "Title": title, "URL": link, "ASIN": asin})

                # 显示搜索结果在主区域
                st.subheader(f"搜索结果显示{max_links}条，如有问题，请联系管理员")
                results_df = pd.DataFrame(st.session_state.results)
                results_df['Title'] = results_df.apply(lambda row: f'<a href="{row["URL"]}">{row["Title"]}</a>', axis=1)
                results_df = results_df[['Image', 'Title', 'ASIN']]
                st.markdown(results_df.to_html(escape=False, index=False), unsafe_allow_html=True)

                # 下载按钮
                download_df = results_df[['Title', 'ASIN']].copy()
                download_df['URL'] = [result['URL'] for result in st.session_state.results]
                excel_buffer = BytesIO()
                download_df.to_excel(excel_buffer, index=False, engine='openpyxl')
                excel_buffer.seek(0)

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

    # 显示用户计数器
    if os.path.exists(USER_COUNT_FILE):
        user_count = int(open(USER_COUNT_FILE).read().strip())
        display_user_count(user_count)
    
USER_CREDENTIALS_FILE = "users.txt"

def load_user_credentials():
    """加载存储的用户账号和密码"""
    credentials = {}
    try:
        with open(USER_CREDENTIALS_FILE, 'r') as file:
            for line in file:
                user, pwd = line.strip().split(',')
                credentials[user] = pwd
    except FileNotFoundError:
        pass
    return credentials

def add_new_user(username, password):
    """手动添加新的用户账号和密码"""
    with open(USER_CREDENTIALS_FILE, 'a') as file:
        file.write(f"{username},{password}\n")

def check_user_credentials(username, password):
    """检查用户账号和密码是否正确"""
    credentials = load_user_credentials()
    return credentials.get(username) == password

def check_login():
    """用户登录逻辑"""
    if "logged_in" not in st.session_state:
        st.subheader("用户登录")
        username = st.text_input("请输入账号")
        password = st.text_input("请输入密码", type="password")

        if st.button("登录"):
            if check_user_credentials(username, password):
                st.success("登录成功！")
                st.session_state.logged_in = True
                
                update_user_count()  

            else:
                st.error("账号或密码错误，请重试")

    return st.session_state.get("logged_in", False)

if __name__ == "__main__":
    # 登录页
    if check_login():
        main()
    else:
        st.markdown("""
    <div style="font-weight: bold; color: #ff0000; background-color: #f0f0f0; padding: 10px;">
        为了提供更优质的服务，请扫码进入微信群免费获取账号密码
    </div>
""", unsafe_allow_html=True)
        st.image("image/wechat.jpg",width=300,caption="扫码添加管理员微信")