import streamlit as st
import pandas as pd
from io import BytesIO
import time
import random
import requests
from bs4 import BeautifulSoup
from utils import google_search, bing_search
import os

# Add custom CSS to hide the GitHub icon
hide_github_icon = """
.st-emotion-cache-1wbqy5l e3g6aar2 {
  visibility: hidden;
}
"""

# List of user agents to randomize the header for each request
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.54',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0'
]

# Path to the file storing user count
USER_COUNT_FILE = "user_count.txt"

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

def update_user_count():
    """Update and return the current user count."""
    if not os.path.exists(USER_COUNT_FILE):
        # If file doesn't exist, create it with the initial value
        with open(USER_COUNT_FILE, "w") as f:
            f.write("735")
    
    # Read current count
    with open(USER_COUNT_FILE, "r") as f:
        user_count = int(f.read().strip())
    
    # Increment count
    user_count += 1
    
    # Save the updated count back to the file
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
    st.write("遇到问题联系：happy_prince45")
    st.subheader("搜索设置")
    search_engine = st.selectbox("选择搜索引擎", ["Google", "Bing"])
    amazon_site = st.selectbox("选择亚马逊站点", [
        "amazon.com", "amazon.ca", "amazon.co.uk", "www.amazon.com.au", 
        "www.amazon.in", "www.amazon.sg", "www.amazon.ae"
    ])
    keyword = st.text_input("输入关键词")
    max_links = st.slider("查询链接数限制", 3, 15, 5)  # Allow user to set maximum number of links to fetch

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
                    image_url = extract_image_url(asin) if asin else None
                    # Use default image if no image found
                    image_tag = f'<img src="{image_url}" style="width:100px;height:100px;object-fit:cover;"/>' if image_url else f'<img src="https://ninjify.shop/wp-content/uploads/2024/08/微信图片_20240831012417.jpg" style="width:100px;height:100px;object-fit:cover;"/>'
                    st.session_state.results.append({"Image": image_tag, "Title": title, "URL": link, "ASIN": asin})

                st.subheader(f"搜索结果-试用版限制{max_links}条，如果要取消限制，请联系管理员")
                
                # Display results in table format
                results_df = pd.DataFrame(st.session_state.results)
                results_df['Title'] = results_df.apply(lambda row: f'<a href="{row["URL"]}">{row["Title"]}</a>', axis=1)
                results_df = results_df[['Image', 'Title', 'ASIN']]  # Arrange columns as required
                
                st.markdown(results_df.to_html(escape=False, index=False), unsafe_allow_html=True)
                
                # Prepare DataFrame for download (without Image URL)
                download_df = results_df[['Title', 'ASIN']].copy()
                download_df['URL'] = [result['URL'] for result in st.session_state.results]
                excel_buffer = BytesIO()
                download_df.to_excel(excel_buffer, index=False, engine='openpyxl')
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
    st.image("image/publicwechat.jpg")

    # Display the user count at the bottom left corner
    user_count = int(open(USER_COUNT_FILE).read().strip())  # Read the current count
    display_user_count(user_count)

def check_password():
    """Returns `True` if the user enters the correct password."""
    if "password_correct" not in st.session_state:
        st.subheader("用户认证")
        password = st.text_input("请输入密码", type="password")
        if st.button("提交"):
            if password == "happyprince":  # Set password to 'happyprince'
                st.session_state.password_correct = True
                # Update and display user count after correct password submission
                user_count = update_user_count()
                display_user_count(user_count)
            else:
                st.error("密码错误，请重试")
                st.session_state.password_correct = False

    return st.session_state.get("password_correct", False)

if __name__ == "__main__":
    # Display the user count at the bottom left corner of the password page
    user_count = int(open(USER_COUNT_FILE).read().strip())  # Read the current count
    display_user_count(user_count)

    if check_password():
        main()
    else:
        st.warning("由于服务器资源有限，为避免不必要流量，请进入官方群或关注微信公众号“Hapince出海日记”获取密码")
        st.image("image/publicwe.jpg")
