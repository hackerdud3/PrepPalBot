import os
import openai
import asyncio
import playwright.async_api as playwright
import streamlit as st
from langchain_openai import OpenAI
from dotenv import load_dotenv
from openai import OpenAI
from langchain_openai import ChatOpenAI
from rag import get_index_for_pdf
from url_loader_and_splitter import get_url_index
from streamlit_chat import message
from langchain.chains.conversation.base import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate, MessagesPlaceholder
load_dotenv()

response_types = {
    'Generate Questions' : """
        You are a helpful assistant who will train users on personalized interview questions. Your goal is to generate questions based on the context above passed to you.
        Context include parsed data from websites. Provide questions if only relavant context is passed.
        Otherwise, reply "Relavant data is not found for generating Interview questions" if context is irrelevant.

        % START OF DATA FROM WEBSITE
        {context}
        % END OF DATA FROM WEBSITE
""" ,
    'Answer Questions' : """
        You are a helpful Assistant who will train users on personalized interview questions. You will provide the best possible answer to the interview question based on the context passed to you.
"""
}
map_prompt =  """
    You are helpful AI assistant that trains the user on personalized interview questions.

    {response_type}

    % START OF RESUME INFORMATION
    {context}
    % END OF RESUME INFORMATION
"""

combined_prompt = """
    You are a helpful Assistant who will train users on personalized interview questions.
    You will be given information about candidate's {resume}.
    

"""


prompt_template = """
    You are a helpful Assistant who will train users on personalized interview questions. You will provide users with 10 personalized interview questions based on the context passed to you. The context here is data from 
    from a Interview questions website.

    When the {input} is an interview question. Provide best possible answer to the interview question provided to you for the user to answer based on the context. You need to provide your answer based on multiple contexts, for example resume context, given to you.


    Reply "Relavant information for the question is not provided" if context is irrelevant.
        
     
"""

system_msg_template = SystemMessagePromptTemplate.from_template(
    template=prompt_template)

human_msg_template = HumanMessagePromptTemplate.from_template(
    template="{input}")

chat_prompt_template = ChatPromptTemplate.from_messages(
    [system_msg_template, human_msg_template, MessagesPlaceholder(variable_name="history")])

urls = []

# Initializing OPENAI client


def initialize_openai_client():
    return ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-3.5-turbo-1106", temperature=0.5)


def create_conversation_chain(llm):
    return ConversationChain(
        memory=st.session_state.buffer_memory, prompt=chat_prompt_template, llm=llm, verbose=True
    )

# Ask a question


def ask_question():
    return st.chat_input("Ask a question", key="input")


def generate_questions():
    pass


def input_urls():
    for i in range(3):
        url = st.sidebar.text_input(
            f"URL {i+1}", placeholder="https://www.example.com")
        urls.append(url)

# Upload PDF files


def upload_pdf_files():
    pdf_file = st.file_uploader("", type="pdf", accept_multiple_files=False)
    return pdf_file

# find match


def find_match(vector_index, query):
    search_results = vector_index.similarity_search_with_score(
        query=query, k=10)
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
            k=3, return_messages=True, memory_key='history')

    response_container = st.container()
    text_container = st.container()

    # Chat model
    llm = initialize_openai_client()

    # Buffer memory
    if "buffer" not in st.session_state:
        st.session_state.buffer = ConversationBufferWindowMemory(
            k=3, return_messages=True)

    # Upload PDF files
    pdf_files = upload_pdf_files()

    # Get index for PDF
    if pdf_files:
        file_content = pdf_files.getvalue()
        vector_index = get_index_for_pdf([file_content])
    else:
        st.error("Please upload a PDF file")

    # Url loader

    process_urls = st.sidebar.button("Generate Interview Questions")
    if process_urls and len(urls) > 0:
        url_index = get_url_index(urls[0])
    else:
        st.error("Please enter atleast one URL")

    # Conversation chain
    conversation_chain = create_conversation_chain(llm)

    # Ask question
    with text_container:
        query = ask_question()
        if query:
            with st.spinner("Typing..."):
                conversation_string = get_conversation_string()
                # Similarity search
                context = find_match(vector_index, query)
                pdf_extract = ""
                for i in range(len(context)):
                    doc = context[i][0]
                    pdf_extract += doc.page_content[:500]
                prompt_template.format(pdf_extract=pdf_extract)
                # response = conversation_chain.predict(
                #     input=f"Context:\n {pdf_extract} \n\n Query:\n{query}")

                response = conversation_chain.predict(
                   "Query": query )
            st.session_state.requests.append(query)
            st.session_state.responses.append(response)

    with response_container:
        if st.session_state['responses']:
            for i in range(len(st.session_state["responses"])):
                message(st.session_state["responses"][i], key=str(i))
                if i < len(st.session_state["requests"]):
                    message(st.session_state["requests"][i],
                            is_user=True, key=str(i) + "_user")


if __name__ == '__main__':

    main()
