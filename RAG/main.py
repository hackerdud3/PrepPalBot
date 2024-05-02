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
from url_loader_and_splitter import get_url_chunks, get_info_from_url
from streamlit_chat import message
from langchain.chains.conversation.base import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
load_dotenv()

response_types = {
    'Generate Questions': """
        You are a helpful assistant who will train users on personalized interview questions. Your goal is to generate questions based on the context above passed to you.
        Provide questions if only relavant context is passed.
        Otherwise, reply "Relavant data is not found for generating Interview questions" if context is irrelevant.
""",
    'Answer Questions': """
        You are a helpful Assistant who will train users on personalized interview questions. You will provide the best possible answer to the interview question based on the context passed to you.
"""
}


map_prompt = """
    You are helpful AI assistant that trains the user on personalized interview questions.
    The below context is from a Interview questions website. Please identify intreview questions and its answers.

    {response_type}
    
    % START OF CONTEXT 
    {text}
    % END OF CONTEXT

    Your Response: """
map_prompt_template = PromptTemplate(
    template=map_prompt, input_variables=["text", "response_type"])


combined_prompt = """
    You are a helpful Assistant who will train users on personalized interview questions.
    Do not make anything up, only use information provided in the context.

    {response_type}

    % START OF CONTEXT
    {text}
    % END OF CONTEXT
"""

combined_prompt_template = PromptTemplate(
    template=combined_prompt, input_variables=["text", "response_type"])


prompt_template = """
    You are a helpful Assistant who will provide answers to users on personalized interview questions. 
    Provide best possible answer to the interview question based on the context.

    If you don't have enough information to answer the question, you can reply what information related to the question is missing the resume and provide example of how to answer to that question..

    % Here are few examples on how you will answer
    Example 1:
    Query: How Do You Handle a Situation Where You Have to Meet Multiple Deadlines?
    Answer: When faced with simultaneous project deadlines, I lean on my prioritization skills. For instance, at my last job, I organized tasks by urgency and impact, allocating time to each based on their deadline and importance. I managed to submit all projects on time without compromising on quality.

    Example 2:
    Query: Tell me about yourself and your qualifications
    Answer: I’ve been a bookkeeper for the past three years where I track accounts payable and receivable, as well as oversee payroll. I’ve been able to find and resolve discrepancies between amounts owed and received, which has ended up saving our company thousands of dollars in underpaid bills. I recently earned my CPA degree and think my experience with bookkeeping and attention to detail would make me a great fit for your open public accountant role.

"""

system_msg_template = SystemMessagePromptTemplate.from_template(
    template=prompt_template, input_variables=["input"])

human_msg_template = HumanMessagePromptTemplate.from_template(
    template="{input}")

chat_prompt_template = ChatPromptTemplate.from_messages(
    [system_msg_template, human_msg_template, MessagesPlaceholder(variable_name="history")])

urls = []

output_type = ""


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
    for i in range(1):
        url = st.sidebar.text_input(
            f"URL {i+1}", placeholder="https://www.example.com")
        urls.append(url)

# Upload PDF files


def upload_pdf_files():
    pdf_file = st.file_uploader("", type="pdf", accept_multiple_files=False)
    return pdf_file


def find_match(vector_index, query):
    search_results = vector_index.similarity_search_with_score(
        query=query, k=3, pre_filter={"resumeid": {"$eq": 1}})
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
            k=0, return_messages=True, memory_key='history')

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

    # Load summarization chain
    chain = load_summarize_chain(llm,
                                 chain_type="map_reduce",
                                 map_prompt=map_prompt_template,
                                 combine_prompt=combined_prompt_template,
                                 )
    # Url loader

    process_urls = st.sidebar.button("Generate Interview Questions")
    try:
        if process_urls and len(urls) > 0:
            # output_type = "Generate Questions"
            url_chunks = get_url_chunks(urls[0])
            url_data = ""
            url_data = get_info_from_url(urls[0])

            output = chain.invoke(
                {"input_documents": url_chunks, "response_type": "Generate Questions"})
            print(combined_prompt.format)
            st.sidebar.write(output)
        else:
            st.error("Please enter atleast one URL")
    except Exception as e:
        st.error(f"Error processing URL")

    # Conversation chain
    conversation_chain = create_conversation_chain(llm)

    # Ask question
    with text_container:
        query = ask_question()
        if query:
            with st.spinner("Typing..."):
                conversation_string = get_conversation_string()
                # Similarity search
                docs = find_match(vector_index, query)
                st.write(docs)

                pdf_extract = ""
                for i in range(len(docs)):
                    doc = docs[i][0]
                    pdf_extract += doc.page_content
                response = conversation_chain.predict(
                    input=f"Context:\n {pdf_extract} \n\n Query:\n{query}")

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
