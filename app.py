import streamlit as st
import pandas as pd
from utils import google_search, bing_search

def main():
    st.title("亚马逊僵尸链接查询工具 - Hapince出海专供（试用版本）")

    st.sidebar.subheader("搜索设置")
    search_engine = st.sidebar.selectbox("选择搜索引擎", ["Google", "Bing"])
    amazon_site = st.sidebar.selectbox("选择亚马逊站点", [
        "amazon.com", "amazon.ca", "amazon.co.uk", "www.amazon.com.au", 
        "www.amazon.in", "www.amazon.sg", "www.amazon.ae"
    ])
    keyword = st.sidebar.text_input("输入关键词")

    if st.sidebar.button("搜索"):
        st.subheader(f"搜索结果 ({search_engine})")
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


    st.sidebar.subheader("联系方式")
    st.sidebar.write("关注公众号“Hapince出海日记”")
    st.sidebar.write("或添加客服微信：happy_prince45")

if __name__ == "__main__":
    main()
