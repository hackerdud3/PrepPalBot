from typing import List
from langchain.document_loaders.async_html import AsyncHtmlLoader
from langchain.document_transformers.beautiful_soup_transformer import BeautifulSoupTransformer
from langchain.document_transformers.html2text import Html2TextTransformer
import streamlit as st


def scrape_urls(urls: List[str]):
    # Load HTML
    st.write(urls)
    loader = AsyncHtmlLoader(urls)
    html = loader.load()

    # Transform HTML
    bs_transformer = BeautifulSoupTransformer()
    docs = bs_transformer.transform_documents(html)
    st.write(docs[0].page_content)[0:500]
    return docs
