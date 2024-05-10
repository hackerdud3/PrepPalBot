import re
import streamlit as st
from io import BytesIO
from typing import Tuple, List
from pypdf import PdfReader
from mongoDBclient import client
from langchain.docstore.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_mongodb import MongoDBAtlasVectorSearch
from load_summarize_chain import load_summarize


db_name = "careercoach"
collection_name = "pdf_embeddings"
atlas_collection = client[db_name][collection_name]
vector_search_index = "pdf_index"

# Parse pdf file


def parse_pdf(file: BytesIO) -> Tuple[List[str]]:
    pdf = PdfReader(file)
    output = []
    i = 0
    for page in pdf.pages:
        text = page.extract_text()
        text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)
        text = re.sub(r'\n*•\s*', ' ', text)
        text = re.sub(r"(?<!\n\s)\n(?!\s\n)", "\n", text.strip())
        text = re.sub(r"\n\s*\n", "\n\n", text)
        output.append(text)
    return output

# Convert text to chunks


def text_to_chunks(text, resumeid) -> List[Document]:
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
                page_content=chunk,
                metadata={
                    "page": doc.metadata["page"], "chunk": i, "resumeid": resumeid}
            )
            metadata = f"{doc.metadata['page']}-{doc.metadata['chunk']}"
            doc.metadata["source"] = metadata
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


def get_index_for_pdf(pdf_files, resumeid, llm):
    documents = []
    for pdf_file in pdf_files:
        text = parse_pdf(BytesIO(pdf_file))

    doc = Document(page_content=text[0], metadata={"chunk": 0})
    summarized_pdf = load_summarize([doc], llm)
    st.session_state["summarized_pdf"] = summarized_pdf
    if "summarized_pdf" in st.session_state["summarized_pdf"]:
        st.markdown("###Resume Summary:")
        st.warning(summarized_pdf)
    documents.extend(text_to_chunks(summarized_pdf, resumeid))
    index = vector_store(documents)
    return index
