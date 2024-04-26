from typing import List
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores.mongodb_atlas import MongoDBAtlasVectorSearch
from langchain.docstore.document import Document
import streamlit as st
from mongoDBclient import client
from langchain_community.vectorstores import FAISS


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
    st.write(text)
    return text


def url_splitter(data):
    splitter = RecursiveCharacterTextSplitter(chunk_size=2000, separators=[
                                              "\n\n", "\n", ".", "!", ",", " ", "", "|"], chunk_overlap=10)
    chunks = splitter.create_documents([data])
    return chunks

embeddings = OpenAIEmbeddings()
def faiss_vector_store(docs):
    db = FAISS.from_documents(
        docs, embeddings
    )
    return db

def vector_store(docs: List[Document]):
    vector_search = MongoDBAtlasVectorSearch.from_documents(
        documents=docs,
        embedding=OpenAIEmbeddings(disallowed_special=()),
        collection=atlas_collection,
        index_name=vector_search_index,
    )
    return vector_search

def get_url_chunks(url:str):
    data = get_info_from_url(url)
    url_chunks = url_splitter(data)
    return url_chunks


def get_url_index(url:str):
    data = get_info_from_url(url)
    url_data_chunks = url_splitter(data)
    # index = faiss_vector_store(url_data_chunks)
    # query = "Get all the interview questions and anwers pairs"
    url_index = vector_store(url_data_chunks)

    return url_index
