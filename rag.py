import re
from io import BytesIO
from typing import Tuple, List
import pickle
import streamlit as st
from langchain.docstore.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_mongodb import MongoDBAtlasVectorSearch
from pypdf import PdfReader
from mongoDBclient import client


db_name = "careercoach"
collection_name = "pdf_embeddings"
atlas_collection = client[db_name][collection_name]
vector_search_index = "vector_index"

# Parse pdf file


def parse_pdf(file: BytesIO) -> Tuple[List[str]]:
    pdf = PdfReader(file)
    output = []
    for page in pdf.pages:
        text = page.extract_text()
        text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)
        text = re.sub(r'\n*•\s*', ' ', text)
        text = re.sub(r"(?<!\n\s)\n(?!\s\n)", "\n", text.strip())
        text = re.sub(r"\n\s*\n", "\n\n", text)
        output.append(text)
    return output

# Convert text to chunks


def text_to_chunks(text: List[str]) -> List[Document]:
    if isinstance(text, str):
        text = [text]
    page_docs = [Document(page_content=page) for page in text]
    for i, doc in enumerate(page_docs):
        doc.metadata["page"] = i + 1

    doc_chunks = []
    for doc in page_docs:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=20,
        )
        chunks = text_splitter.split_text(doc.page_content)
        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk, metadata={
                    "page": doc.metadata["page"], "chunk": i}
            )
            doc.metadata["source"] = f"{doc.metadata['page']}-{doc.metadata['chunk']}"
            doc_chunks.append(doc)

    return doc_chunks

# Vector store and return index


def vector_store(docs: List[Document]):
    vector_search = MongoDBAtlasVectorSearch.from_documents(
        documents=docs,
        embedding=OpenAIEmbeddings(disallowed_special=()),
        collection=atlas_collection,
        index_name=vector_search_index,
    )
    return vector_search


def get_index_for_pdf(pdf_files):
    documents = []
    for pdf_file in pdf_files:
        text = parse_pdf(BytesIO(pdf_file))
        documents = documents + text_to_chunks(text)
    index = vector_store(documents)
    return index
