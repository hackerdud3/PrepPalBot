from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter

import streamlit as st
from langchain.document_loaders.url_selenium import SeleniumURLLoader


main_placeholder = st.empty()


def load_data_from_urls(urls: List[str]):
    try:
        main_placeholder.text("Loading data from urls...")
        loader = SeleniumURLLoader(urls=urls)
        data = loader.load()
    except Exception as e:
        main_placeholder.text(
            "Error loading data from urls. Please try again.")
    return data


def url_splitter(data: List[str]):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, separators=[
                                              "\n\n", "\n", ".", "!", "?", ",", " ", ""], chunk_overlap=10)
    chunks = splitter.split_documents(data)
    return chunks
