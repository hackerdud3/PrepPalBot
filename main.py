import os
import openai
import asyncio
import playwright.async_api as playwright
import streamlit as st
from langchain_openai import OpenAI
from dotenv import load_dotenv
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from rag import get_index_for_pdf
from html_scrape import scrape_urls
from url_loader_and_splitter import load_data_from_urls, url_splitter
from streamlit_chat import message
from langchain.chains.conversation.base import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate, MessagesPlaceholder

prompt_template = """
    You are a helpful Assistant who answers and provides feedback to users answers on interview questions based on multiple contexts given to you.

    Keep your response and to the point according to the context.
    
    The evidence are the context of the pdf extract, which is users resume, with metadata. 
        
    Reply "Not applicable" if text is irrelevant.
     
"""

system_msg_template = SystemMessagePromptTemplate.from_template(
    template=prompt_template)

human_msg_template = HumanMessagePromptTemplate.from_template(
    template="{query}")

chat_prompt_template = ChatPromptTemplate.from_messages(
    [system_msg_template, human_msg_template])

urls = []

# Initializing OPENAI client


def initialize_openai_client():
    load_dotenv()
    return ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-3.5-turbo-1106", temperature=0.2)


def create_conversation_chain(llm):
    return ConversationChain(
        memory=st.session_state.buffer_memory, prompt=chat_prompt_template, llm=llm, verbose=True
    )

# Ask a question


def ask_question():
    return st.chat_input("Ask a question", key="question")


def generate_questions():
    pass


def input_urls():
    for i in range(3):
        url = st.sidebar.text_input(f"URL {i+1}")
        st.write(url)
        urls.append(url)

# Upload PDF files


def upload_pdf_files():
    pdf_file = st.file_uploader("", type="pdf", accept_multiple_files=False)
    return pdf_file

# find match


def find_match(vector_index, query):
    search_results = vector_index.similarity_search_with_score(
        query=query, k=25)
    return search_results

# Conversation string


def get_conversation_string():
    conversation_string = ""
    for i in range(len(st.session_state["responses"]) - 1):
        conversation_string += "Human: " + \
            st.session_state['requests'][i] + "\n"
        conversation_string += "Bot: " + \
            st.session_state['responses'][i+1] + "\n"
    return conversation_string


def main():
    st.title("Career Coach")

    input_urls()

    if "responses" not in st.session_state:
        st.session_state["responses"] = ["How can I assist you today?"]

    if "requests" not in st.session_state:
        st.session_state["requests"] = []

    if "buffer_memory" not in st.session_state:
        st.session_state.buffer_memory = ConversationBufferWindowMemory(
            k=3, return_messages=True)

    response_container = st.container()
    text_container = st.container()

    # Chat model
    llm = initialize_openai_client()

    # Upload PDF files
    pdf_files = upload_pdf_files()

    vector_index = None

    # Get index for PDF
    if pdf_files:
        file_content = pdf_files.getvalue()
        vector_index = get_index_for_pdf([file_content])
        st.write(pdf_files)
    else:
        st.error("Please upload a PDF file")

    # Buffer memory
    if "buffer" not in st.session_state:
        st.session_state.buffer = ConversationBufferWindowMemory(
            k=3, return_messages=True)

    # Url loader
    process_urls = st.sidebar.button("Process")
    if process_urls:
        url_data = load_data_from_urls(urls)
        url_data_chunks = url_splitter(url_data)

    # # Conversation chain
    # conversation_chain = create_conversation_chain(llm)

    # Ask question
    with text_container:
        query = ask_question()
        if query:
            with st.spinner("Typing..."):
                conversation_string = get_conversation_string()
                # Similarity search
                context = find_match(vector_index, query)
                pdf_extract = "/n ".join(
                    [result.page_content for result in context])
                prompt_template.format(pdf_extract=pdf_extract)
                # prompt_input = {
                #     "query": f"Context:\n{pdf_extract} \n\n Query:\n{query}"
                # }
                # response = conversation_chain.predict(
                #     input={prompt_input})
            st.session_state.requests.append(query)
            st.session_state.responses.append(response)
    with response_container:
        if st.session_state['responses']:
            for i in range(len(st.session_state["responses"])):
                message(st.session_state["responses"][i], key=str(i))
                if i < len(st.session_state["requests"]):
                    message(st.session_state["requests"][i],
                            is_user=True, key=str(i) + "_user")
    # Call ChatGPT with streaming and display the response as it comes

        # for chunk in openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo", messages=prompt, stream=True
        # ):
        #     text = chunk.choices[0].get("delta", {}).get("content")
        #     if text is not None:
        #         response.append(text)
        #         result = "".join(response).strip()
        #         botmsg.write(result)

        # # Add the assistant's response to the prompt
        # prompt.append({"role": "assistant", "content": result})


if __name__ == '__main__':

    main()
