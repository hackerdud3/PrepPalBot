import re
import os
import streamlit as st
from io import BytesIO
import os
import time
from PyPDF2 import PdfFileReader
from dotenv import load_dotenv
from typing import Tuple, List
from pypdf import PdfReader
from mongoDBclient import client
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_mongodb import MongoDBAtlasVectorSearch
from load_resume_summarize_chain import load_summarize
from langchain_pinecone import PineconeEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.embeddings import OpenAIEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
import spacy
import re

load_dotenv()

db_name = os.getenv("MONGODB_DATABASE")
collection_name = os.getenv("MONGODB_EMBEDDING_COLLECTION")
atlas_collection = client[db_name][collection_name]
vector_search_index = os.getenv("MONGODB_VECTOR_SEARCH_INDEX")
pc_index = os.getenv("PINECONE_INDEX_NAME")


# Parse PDF
def parse_pdf(file):
    pdf_reader = PdfReader(file)
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
        text = re.sub(r"(\w+)-(\w+)", r"\1\2", text)
        text = re.sub(r'\n*•\s*', ' ', text)
        text = re.sub(r"(?<!\n\s)\n(?!\s\n)", "\n", text.strip())
        text = re.sub(r"\n\s*\n", "\n\n", text)
    return text


def text_to_chunks(text, resumeid) -> List[Document]:
    if isinstance(text, str):
        text = [text]
    page_docs = [Document(page_content=page) for page in text]
    for i, doc in enumerate(page_docs):
        doc.metadata["page"] = i + 1

    doc_chunks = []
    for doc in page_docs:

        pattern = r"(\n\n(?:[A-Z\s]+)\n\n)" 
        chunks = re.split(pattern, doc.page_content) 
      
        combined_chunks = []
        current_chunk = ""
        for chunk in chunks:
            if re.match(pattern, chunk):  
                if current_chunk:
                    combined_chunks.append(current_chunk)
                current_chunk = chunk  
            else:
                current_chunk += chunk  
        
        if current_chunk:  
            combined_chunks.append(current_chunk)

        for i, chunk in enumerate(combined_chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    "page": doc.metadata["page"], "chunk": i, "resumeid": resumeid
                }
            )
            metadata = f"{doc.metadata['page']}-{doc.metadata['chunk']}"
            doc.metadata["source"] = metadata
            doc_chunks.append(doc)

    return doc_chunks


# Convet text to documents
def text_to_docs(text, resumeid) -> List[Document]:
    if isinstance(text, str):
        text = [text]
    page_docs = [Document(page_content=page) for page in text]
    for i, doc in enumerate(page_docs):
        doc.metadata["page"] = i + 1

    doc_chunks = []
    for doc in page_docs:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=0,
            separators=["?"] 
        )
        chunks = text_splitter.split_text(doc.page_content)

        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    "page": doc.metadata["page"], "chunk": i, "resumeid": resumeid}
            )
            metadata = f"{doc.metadata['page']}-{doc.metadata['chunk']}"
            doc.metadata["source"] = metadata
            doc_chunks.append(doc)

    return doc_chunks

# Vector store and return index

# def vector_store(docs: List[Document]):
#     vector_search = PineconeVectorStore.from_documents(
#         documents=docs,
#         embedding= PineconeEmbeddings(model="text-embedding-ada-002", api_key=os.getenv("PINECONE_API_KEY")),
#         index_name=pc_index,
#         namespace="resumes"
#     )
#     return vector_search


# def get_instance_for_atlas_search(text, resumeid):
#     documents = []
#     documents.extend(text_to_chunks(text, resumeid))
#     extract_text = ""
#     for doc in documents:
#         extract_text += doc.page_content
#     search_instance = vector_store(documents)
#     return search_instance

def pinecone_vector_store(text, resumeid):
    documents = []
    documents.extend(text_to_docs(text, resumeid))
    st.write(documents)
    vector_search = PineconeVectorStore.from_documents(documents=documents, embedding= OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY")), index_name=pc_index, namespace=resumeid)