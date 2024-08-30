import streamlit as st
import pandas as pd
from io import BytesIO
from utils import google_search, bing_search

def extract_asin(url):
    """Extract ASIN from Amazon product URL."""
    if "dp/" in url:
        parts = url.split("dp/")
        if len(parts) > 1:
            asin_part = parts[1].split('/')[0][:10]  # Extract only the first 10 characters
            return asin_part
    return None

def fetch_all_results(search_engine, keyword, amazon_site, max_pages=10):
    """Fetch results from all pages until no more results or max_pages is reached."""
    page = 0
    all_results = []
    
    while page < max_pages:
        if search_engine == "Google":
            results = google_search(keyword, amazon_site, page)
        elif search_engine == "Bing":
            results = bing_search(keyword, amazon_site, page)
        
        # If no more results are found, break the loop
        if not results:
            break

        all_results.extend(results)
        page += 1
    
    return all_results

def main():
    st.title("亚马逊僵尸链接查询工具 - （试用版本）")
    st.write("添加微信“happy_prince45获取全功能僵尸链接采集软件”。1.查询链接条数无限制2.查询结果包含品牌评分3.可以一件导出asin4.多站点查询.......")
    st.subheader("搜索设置")
    search_engine = st.selectbox("选择搜索引擎", ["Google", "Bing"])
    amazon_site = st.selectbox("选择亚马逊站点", [
        "amazon.com", "amazon.ca", "amazon.co.uk", "www.amazon.com.au", 
        "www.amazon.in", "www.amazon.sg", "www.amazon.ae"
    ])
    keyword = st.text_input("输入关键词")
    max_pages = st.slider("查询页数限制", 1, 20, 10)  # Allow user to set maximum number of pages to fetch

    if st.button("搜索"):
        # Fetch results from all pages
        all_results = fetch_all_results(search_engine, keyword, amazon_site, max_pages)

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
