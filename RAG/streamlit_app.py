import os
import time
import streamlit as st
from typing import List
from dotenv import load_dotenv
from mongoDBclient import client
from langchain_openai import ChatOpenAI
from rag import get_index_for_pdf
from url_loader_and_splitter import get_url_chunks, get_url_index
from streamlit_chat import message
from langchain.chains.llm import LLMChain
from url_loader_and_splitter import questions_text_splitter
from langchain.chains.conversation.base import ConversationChain
from langchain.chains.combine_documents.reduce import ReduceDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.chains.summarize import load_summarize_chain
from langchain.chains.combine_documents.map_reduce import MapReduceDocumentsChain
from langchain.chains.combine_documents.stuff import create_stuff_documents_chain
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate, MessagesPlaceholder, PromptTemplate

load_dotenv()

# MongoDB collection
database = client["careercoach"]
collection = database["resumes"]


response_types = {
    'Generate Questions': """
        You are a helpful assistant who will train users on personalized interview questions. Your goal is to generate questions based on the context above passed to you.
        Provide questions if only relavant context is passed.
        Otherwise, reply "Relavant data is not found for generating Interview questions" if context is irrelevant.
""",
    'Answer Questions': """
        You are a helpful Assistant who will train user on personalized interview questions. You will provide the best possible answer to the interview question given to you based on the context passed to you.
"""
}

prompt_template = """
As a helpful Assistant, your role is to provide tailored answers to users' interview questions. Craft the best possible answer based on the given context.
The context is the entire summary of the users resume. You need to provide your answer as the user, based on his work experience, skills, etc from the resume.

Use golden rules while providing the response, include situation, tasks, action, and result in the answer.

Keep your response at right length, we have only 30 seconds to answer in an interview setting .

If you lack sufficient information to answer a question, you can highlight what should be include in the answer to deliver it in a best possible way. 
Only answer the question according to the context. Otherwise train the user on how to answer to that interview question with an example answer.

````````````````````````````````````````````````````
Example of how to answer this interview question

Example 1:
Interview Question: How do you handle a situation where you have to meet multiple deadlines?
Answer: When I'm faced with simultaneous project deadlines, I rely on my prioritization skills. For example, in my previous role, 
I meticulously organized tasks based on their urgency and importance, allocating time accordingly. This approach enabled me to meet 
all deadlines without compromising quality.

Example 2:
Interview Question: Describe a Time You Faced a Significant Challenge at Work?
Answer: Last year, our team was on the verge of missing a critical deadline for a new client, which could have derailed the entire 
project. I spearheaded an emergency plan that involved reassigning tasks based on each team member’s strengths and streamlining our 
communication process. It was challenging, but by fostering a collaborative environment and keeping morale high, we delivered quality 
work on time. This experience taught me the importance of adaptability and clear communication in crisis management.”
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
    return ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-3.5-turbo-0125", temperature=0.2)

# Create conversation chain


def create_conversation_chain(llm):
    return ConversationChain(
        memory=st.session_state.buffer_memory, prompt=chat_prompt_template, llm=llm, verbose=True)

# Input to ask a question


def ask_question():
    return st.chat_input("Ask a question", key="input")

# Generate question from the URL using stuff documents chain


def generate_questions_from_stuffed_docs(url_chunks: List[str]):
    llm = initialize_openai_client()

    prompt_template = """
    You are a helpful assistant tasked with training users on personalized interview questions. Your goal is to identify 10 interview questions and provide corresponding answers based on the context provided below, in a sequential manner.

    Provide questions only if the context is relevant to interviews.

    Your response should follow this format:
    For example:
    1. Interviewer: Tell me about yourself and your qualifications?
    \nAnswer: Certainly! Over the past three years, I've been working as a bookkeeper, where I've managed accounts payable and receivable, along with payroll oversight. I take pride in my ability to identify and resolve discrepancies, leading to substantial cost savings for my company. Recently, I earned my CPA degree, and I'm confident that my expertise in bookkeeping, coupled with my attention to detail, aligns well with the requirements of the public accountant role at your organization.

    %CONTEXT
    {context}

    Interview questions and answers:
    """
    stuff_prompt = PromptTemplate.from_template(prompt_template)

    stuff_chain = create_stuff_documents_chain(llm=llm, prompt=stuff_prompt)

    output = stuff_chain.invoke({"context": url_chunks})

    return output


# Generate questions
def generate_questions_from_website(url_chunks: List[str]):
    llm = initialize_openai_client()

    map_llm_template = """You are a helpful assistant who will train users on personalized interview questions. Your goal is to identify only interview questions and its answers in the following context:
        {context}.

        Provide questions if only relavant context is passed.

        Your response should be in this fashsion:
        For example:
        1. Interviewer: Tell me about yourself and your qualifications?.
        Answer: Certainly! Over the past three years, I've been working as a bookkeeper, where I've managed accounts payable and receivable, along with payroll oversight. I take pride in my ability to identify and resolve discrepancies, leading to substantial cost savings for my company. Recently, I earned my CPA degree, and I'm confident that my expertise in bookkeeping, coupled with my attention to detail, aligns well with the requirements of the public accountant role at your organization.

        Interview questions and answers:"""

    map_llm_prompt = PromptTemplate.from_template(map_llm_template)

    map_chain = LLMChain(llm=llm, prompt=map_llm_prompt)

    reduce_llm_template = """Combine all the interview questions and answers identified from the: {context}
    and provide interview questions and answers in sequential numbers."""
    reduce_llm_prompt = PromptTemplate.from_template(reduce_llm_template)

    reduce_llm_chain = LLMChain(llm=llm, prompt=reduce_llm_prompt)

    combined_documents_chain = StuffDocumentsChain(
        llm_chain=reduce_llm_chain,
        document_variable_name="context"
    )

    reduce_doc_chain = ReduceDocumentsChain(
        combine_documents_chain=combined_documents_chain,
        collapse_documents_chain=combined_documents_chain,
        token_max=4000,
    )

    map_reduce_chain = MapReduceDocumentsChain(
        llm_chain=map_chain,
        reduce_documents_chain=reduce_doc_chain,
        document_variable_name="context",
    )
    output = map_reduce_chain.invoke(url_chunks)

    return output["output_text"]


# Input URLs
def input_urls():
    for i in range(1):
        url = st.sidebar.text_input(
            f"URL {i+1}", placeholder="https://www.example.com")
        urls.append(url)

# Upload PDF files


def upload_pdf_files():
    pdf_file = st.file_uploader("", type="pdf", accept_multiple_files=False)
    return pdf_file


def find_match(vector_index, query, resume_id):
    search_results = vector_index.similarity_search_with_score(
        query=query, k=5, pre_filter={"resumeid": {"$eq": resume_id}})
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
    st.title("💬 Prep Pal")
    st.caption("🚀 A carreer chatbot powered by GPT-4o")

    st.session_state["user_name"] = st.text_input(
        placeholder="User Name", label="User Name")
    pdf_files = upload_pdf_files()
    st.write("Upload your resume to get started")
    isUploaded = st.button("Summarize Resume")

    with st.sidebar:
        "[View the source code](https://github.com/hackerdud3/PrepPalBot)"
        "[![View GitHub source code](https://github.com/codespaces/badge.svg)](https://organic-train-6vxgw7v674jfrr4r.github.dev/)"
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
            k=0, return_messages=True)

    if "summarized_pdf" in st.session_state:
        st.markdown("### Resume Summary:")
        st.warning(st.session_state["summarized_pdf"])

    # Get index for
    if isUploaded and pdf_files is not None:
        # If a new file is uploaded then we need to reset the responses and requests
        st.session_state["responses"] = ["How can I assist you today?"]
        st.session_state["requests"] = []

        if (st.session_state["user_name"] == ""):
            st.error("Please enter a user name")
            return

        with st.spinner("Summarizing your resume..."):
            time.sleep(3)

        resume_info = {
            "user_name": st.session_state["user_name"],
            "file_name": pdf_files.name,
        }

        inserted_data = collection.insert_one(resume_info)
        resume_id = inserted_data.inserted_id
        st.session_state["resume_id"] = str(resume_id)
        file_content = pdf_files.getvalue()

        with st.spinner("Uploading your resume to database..."):
            time.sleep(3)

        if "vector_index" in st.session_state:
            del st.session_state["vector_index"]

        if "vector_index" not in st.session_state:
            vector_index = get_index_for_pdf(
                [file_content], str(resume_id), llm)
            st.session_state["vector_index"] = vector_index

        st.success("Resume uploaded successfully")
        # Store resume information in resumes collection
    elif isUploaded is True and pdf_files is None:
        st.error("Please upload a resume to continue")

    # Url loader
    process_urls = st.sidebar.button("Generate Interview Questions")

    try:
        if process_urls and len(urls) > 0:
            # output_type = "Generate Questions"
            if (st.session_state["user_name"] == ""):
                st.error("Please enter a user name to generate questions")
                return

            url_chunks = get_url_chunks(
                urls[0], st.session_state["user_name"])
            url_chunks = url_chunks[:5]

            with st.spinner("Generating questions..."):

                questions_and_answers = generate_questions_from_stuffed_docs(
                    url_chunks)

                st.session_state["generated_questions"] = questions_and_answers

        elif process_urls is True and len(urls) == 0:
            st.sidebar.error(
                "Please enter atleast one URL to generate questions")

    except Exception as e:
        st.error(e)

    if "generated_questions" in st.session_state:
        st.sidebar.markdown("### Output:")
        st.sidebar.success(st.session_state["generated_questions"])
    # Conversation chain
    conversation_chain = create_conversation_chain(llm)

    # Ask question
    with text_container:
        question = ask_question()
        if question:
            with st.spinner("Typing..."):
                # Similarity search
                v_index = st.session_state["vector_index"]
                resume_id = st.session_state["resume_id"]
                docs = find_match(v_index, question, resume_id)

                pdf_extract = ""
                for i in range(len(docs)):
                    doc = docs[i][0]
                    pdf_extract += doc.page_content

                response = conversation_chain.predict(
                    input=f"Resume Context:\n {pdf_extract} \n\n Interview Question:\n{question}")

            st.session_state.requests.append(question)
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
