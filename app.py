import streamlit as st
import pandas as pd
from utils import google_search, bing_search

def main():
    st.title("亚马逊僵尸链接查询工具 - （试用版本）")
    st.write("移动端用户请点击左上角“>”开始使用")
    st.write("添加微信“happy_prince45获取全功能僵尸链接采集软件”。1.查询链接条数无限制2.查询结果包含品牌评分3.可以一件导出asin4.多站点查询.......")
    st.subheader("搜索设置")
    search_engine = st.selectbox("选择搜索引擎", ["Google", "Bing"])
    amazon_site = st.selectbox("选择亚马逊站点", [
        "amazon.com", "amazon.ca", "amazon.co.uk", "www.amazon.com.au", 
        "www.amazon.in", "www.amazon.sg", "www.amazon.ae"
    ])
    keyword = st.text_input("输入关键词")

    if st.button("搜索"):
        st.subheader(f"搜索结果-试用版限制10条 ({search_engine})")
        page = 0
        results = []

        if search_engine == "Google":
            results = google_search(keyword, amazon_site, page)
        elif search_engine == "Bing":
            results = bing_search(keyword, amazon_site, page)

        if results:
            for i, (title, link) in enumerate(results, start=1):
                st.markdown(f"**{i}. [{title}]({link})**")
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
        st.warning("由于服务器资源有限，为避免不必要流量，请关注微信公众号“Hapince出海日记”获取密码")
