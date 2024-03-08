import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from langchain_community.document_loaders import PyPDFLoader

def initialize_openai_client():
    load_dotenv
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def upload_pdf_files():
    pdf_file = st.file_uploader("", type="pdf", accept_multiple_files=False)
    return pdf_file

def load_pdf(pdf_file):
    loader = PyPDFLoader(pdf_file)
    pages = loader.load_and_split()
    return pages

def main():
    st.title("Career Coach")
    client = initialize_openai_client()
    pdf_file = upload_pdf_files()

    # Load and split pdf
    pages = load_pdf(pdf_file)
    len(pages)
    print(pages[0])

if __name__ == '__main__':
   main()