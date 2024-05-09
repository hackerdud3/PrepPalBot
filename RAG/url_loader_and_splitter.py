from langchain_community.vectorstores import FAISS
from mongoDBclient import client
import streamlit as st
from langchain.docstore.document import Document
from langchain.vectorstores.mongodb_atlas import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from markdownify import markdownify as md
from bs4 import BeautifulSoup
from typing import List
import requests


main_placeholder = st.empty()

db_name = "careercoach"
collection_name = "url_embeddings"
atlas_collection = client[db_name][collection_name]
vector_search_index = "url_index"


# def load_data_from_urls(urls: List[str]):
#     try:
#         main_placeholder.text("Loading data from urls...")
#         loader = SeleniumURLLoader(urls=urls)
#         data = loader.load()
#     except Exception as e:
#         main_placeholder.text(
#             "Error loading data from urls. Please try again.")
#     return data


def get_info_from_url(url: str):
    try:
        response = requests.get(url)
    except:
        return
    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text()
    text = md(text)
    return text


def url_text_splitter(data: str, url: str, username: str):
    splitter = RecursiveCharacterTextSplitter(chunk_size=4000, separators=[
                                              "\n\n", "\n", ".", "!", ",", " ", "", "|", "\d+\."], chunk_overlap=10)
    metadata = {
        "url": url,
        "username": username
    }
    chunks = splitter.create_documents([data], [metadata])
    return chunks


def questions_text_splitter(data: str, url: str, username: str):

    splitter = RecursiveCharacterTextSplitter(chunk_size=400, separators=[
                                              "\n\n", "\d+\."], chunk_overlap=0)
    metadata = {
        "url": url,
        "username": username
    }
    chunks = splitter.create_documents([data], [metadata])
    return chunks


embeddings = OpenAIEmbeddings()


def vector_store(docs: List[Document]):
    vector_search = MongoDBAtlasVectorSearch.from_documents(
        documents=docs,
        embedding=OpenAIEmbeddings(disallowed_special=()),
        collection=atlas_collection,
        index_name=vector_search_index,
    )
    return vector_search


def get_url_chunks(url: str, username: str):
    data = get_info_from_url(url)
    url_chunks = url_text_splitter(data, url, username)
    return url_chunks


def get_url_index(docs: List[Document]):
    url_index = vector_store(docs)
    return url_index
