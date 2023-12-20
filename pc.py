import streamlit as st
import requests
from bs4 import BeautifulSoup
from collections import Counter
import plotly.express as px
import jieba
import re
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from urllib.parse import urljoin
from nltk.tokenize import word_tokenize

def get_text_from_url(url):
    response = requests.get(url)
    response.encoding = 'utf-8'  # 确保正确处理字符编码
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.body.get_text(), soup.body

def get_text_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

def clean_text_for_preview(text):
    text = re.sub('<.*?>', '', text)  # 去除HTML标签
    return text

def clean_text_for_count(text):
    text = re.sub('<.*?>', '', text)  # 去除HTML标签
    text = re.sub('[^\w\s]', '', text)  # 去除标点符号
    text = re.sub('\s', '', text)  # 去除空格
    return text

def get_top_words(text, num_words):
    text = clean_text_for_count(text)
    if any("\u4e00" <= ch <= "\u9fff" for ch in text):  # 检查是否有中文字符
        words = jieba.lcut(text)  # 使用jieba进行中文分词
    else:
        words = word_tokenize(text)  # 使用nltk进行英文分词
    counter = Counter(words)
    return counter.most_common(num_words) if words else []

def draw_pie_chart(word_counts):
    if word_counts:  # 检查word_counts列表是否为空
        words, counts = zip(*word_counts)
        df = pd.DataFrame({'words': words, 'counts': counts})  # 创建数据框
        fig = px.pie(df, values='counts', names='words', title='词频统计', hover_data=['counts'], labels={'counts':'出现次数'})
        return fig
    else:
        return None

def draw_wordcloud(text):
    if text:  # 检查text是否为空
        wordcloud = WordCloud(font_path='simhei.ttf').generate(text)
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        return plt
    else:
        return None

def get_resources(soup, base_url):
    resources = {'images': [], 'videos': []}

    # 提取图片链接
    for img in soup.find_all('img'):
        src = img.get('src')
        if src:
            # 将相对路径转换为绝对路径
            src = urljoin(base_url, src)
            resources['images'].append(src)

    return resources

def main():
    st.title('WordCloud')
    st.sidebar.title('设置')
    input_option = st.radio('请选择输入方式', ['输入网址', '输入文件路径', '上传文件'])
    url = st.text_input('请输入网址') if input_option == '输入网址' else None
    file_path = st.text_input('请输入文件路径') if input_option == '输入文件路径' else None
    uploaded_file = st.file_uploader("上传文件") if input_option == '上传文件' else None
    num_words = st.sidebar.slider('选择单词数量', min_value=1, max_value=100, value=20)
    show_wordcloud = st.sidebar.checkbox('显示词云', value=True)
    show_pie_chart = st.sidebar.checkbox('显示饼图', value=True)
    color = st.sidebar.color_picker('选择词云颜色', '#000000')
    if url:
        text, soup = get_text_from_url(url)
    elif file_path:
        text = get_text_from_file(file_path)
        soup = None
    elif uploaded_file is not None:
        text = uploaded_file.read().decode()
        soup = None
    else:
        text = None
        soup = None
    if text is not None:
        clean_text_preview = clean_text_for_preview(text)
        clean_text_preview = re.sub('\s+', '\n', clean_text_preview)  # 将连续的空格替换为换行
        word_counts = get_top_words(text, num_words)
        fig_pie = draw_pie_chart(word_counts) if show_pie_chart else None
        fig_wordcloud = draw_wordcloud(text) if show_wordcloud else None
        if fig_pie is not None:  # 检查fig_pie是否为空
            st.plotly_chart(fig_pie)
        if fig_wordcloud is not None:  # 检查fig_wordcloud是否为空
            st.pyplot(fig_wordcloud)
        st.text_area("原始文本预览", clean_text_preview, height=200)  # 设置预览框的高度以显示更多内容
        if st.button('保存文本'):  # 添加一个按钮
            with open('C:\\Users\\30305\\Desktop\\爬虫\\news.txt', 'w', encoding='utf-8') as f:  # 打开一个文件
                f.write(clean_text_preview)  # 将文本写入文件
            st.success('文本已保存到本地')
        if soup is not None:
            st.text("图像捕获")
            resources = get_resources(soup, url)
            for img in resources['images']:
                try:
                    st.image(img, use_column_width=True)
                except Exception as e:
                    st.write(f"无法加载图片：{img}")

if __name__ == "__main__":
    main()
