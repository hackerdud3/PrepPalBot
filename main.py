import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from rag import get_index_for_pdf
from langchain_community.document_loaders import UnstructuredHTMLLoader

prompt_template = """
    You are a helpful Assistant who answers and provides feedback to users answers on interview questions based on multiple contexts given to you.

    Keep your response and to the point according to the context.
    
    The evidence are the context of the pdf extract, which is users resume, with metadata. 
    
    Carefully focus on the metadata specially 'filename' and 'page' whenever answering.
    
    Make sure to add filename and page number at the end of sentence you are citing to.
        
    Reply "Not applicable" if text is irrelevant.
     
    The PDF content is:
    {pdf_extract}
"""

urls = []


# Initializing OPENAI client
def initialize_openai_client():
    load_dotenv()
    return ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-3.5-turbo-1106", temperature=0.2)

# Ask a question


def ask_question():
    return st.chat_input("Ask a question", key="question")


def generate_questions():
    for i in range(3):
        url = st.sidebar.text_input(f"URL {i+1}")
        urls.append(url)

# Upload PDF files


def upload_pdf_files():
    pdf_file = st.file_uploader("", type="pdf", accept_multiple_files=False)
    return pdf_file


@st.cache_data
def create_vectordb(files, filenames):
    # Show a spinner while creating the vectordb
    with st.spinner("Vector database"):
        vectordb = get_index_for_pdf(
            [file.getvalue()
             for file in files], filenames, os.getenv("OPENAI_API_KEY")
        )
    return vectordb


def main():
    st.title("Career Coach")

    # Chat model
    llm = initialize_openai_client()

    # Upload PDF files
    pdf_files = upload_pdf_files()

    if pdf_files:
        pdf_file_names = [file.name for file in pdf_files]
        st.session_state["vectordb"] = create_vectordb(
            pdf_files, pdf_file_names)

    prompt = st.session_state.get(
        "prompt", [{"role": "system", "content": "none"}])

    # Generate questions
    generate_questions()

    question = ask_question()

    if question:
        vectordb = st.session_state.get("vectordb", None)
        if not vectordb:
            with st.message("assistant"):
                st.write("You need to provide a PDF")
                st.stop()

        search_results = vectordb.similarity_search(question, k=3)

        pdf_extract = "/n ".join([result.page_content for result in search_results])

        prompt[0] = {
            "role": "system",
            "content": prompt_template.format(pdf_extract=pdf_extract),
        }

        prompt.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)

    # Display an empty assistant message while waiting for the response
        with st.chat_message("assistant"):
            botmsg = st.empty()

    # Call ChatGPT with streaming and display the response as it comes
        response = []
        result = ""
        for chunk in openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=prompt, stream=True
        ):
            text = chunk.choices[0].get("delta", {}).get("content")
            if text is not None:
                response.append(text)
                result = "".join(response).strip()
                botmsg.write(result)

    # Add the assistant's response to the prompt
        prompt.append({"role": "assistant", "content": result})

    # Store the updated prompt in the session state
        st.session_state["prompt"] = prompt
        prompt.append({"role": "assistant", "content": result})

    # Store the updated prompt in the session state
        st.session_state["prompt"] = prompt


if __name__ == '__main__':
    main()
