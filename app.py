import streamlit as st
import pandas as pd
from utils import google_search, bing_search

def extract_asin(url):
    """Extract ASIN from Amazon product URL."""
    if "dp/" in url:
        parts = url.split("dp/")
        if len(parts) > 1:
            asin_part = parts[1].split('/')[0]
            return asin_part
    return None

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

    if st.button("搜索"):
        page = 0
        if search_engine == "Google":
            results = google_search(keyword, amazon_site, page)
        elif search_engine == "Bing":
            results = bing_search(keyword, amazon_site, page)

        if results:
            # Store results in session state
            st.session_state.results = []
            for title, link in results:
                asin = extract_asin(link)
                st.session_state.results.append({"Title": title, "URL": link, "ASIN": asin})

            st.subheader(f"搜索结果-试用版限制10条 ({search_engine})")
            for i, result in enumerate(st.session_state.results, start=1):
                st.markdown(f"**{i}. [{result['Title']}]({result['URL']})**")
        else:
            st.write("未找到相关结果")

    if "results" in st.session_state and st.session_state.results:
        # Show option to export results
        if st.button("导出为Excel"):
            df = pd.DataFrame(st.session_state.results)
            excel_file = "search_results.xlsx"
            df.to_excel(excel_file, index=False)
            st.success(f"导出成功！文件名：{excel_file}")
            # Provide a download link
            st.download_button(
                label="点击下载",
                data=open(excel_file, "rb").read(),
                file_name=excel_file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

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
