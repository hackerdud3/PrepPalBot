import os
import time
import streamlit as st
from typing import List
from dotenv import load_dotenv
from mongoDBclient import client
from langchain_openai import ChatOpenAI
from rag import get_index_for_pdf
from url_loader_and_splitter import get_url_chunks
from streamlit_chat import message
from langchain.chains.llm import LLMChain
from url_loader_and_splitter import questions_text_splitter
from langchain.chains.conversation.base import ConversationChain
from langchain.chains.combine_documents.reduce import ReduceDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.chains.summarize import load_summarize_chain
from langchain.chains.combine_documents.map_reduce import MapReduceDocumentsChain
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
The context is the entire summary of the users resume. You need to provide your answer as the user based on his work experience, skills, etc from the resume.

If you lack sufficient information to answer a question, you can highlight what should be included in the resume to answer the question in a best possible ways and offer an example on how to address the question effectively.

Here are a few examples of how you might respond:

Example 1:
Interview Question: How do you handle a situation where you have to meet multiple deadlines?
Answer: When I'm faced with simultaneous project deadlines, I rely on my prioritization skills. For example, in my previous role, I meticulously organized tasks based on their urgency and importance, allocating time accordingly. This approach enabled me to meet all deadlines without compromising quality.

Example 2:
Interview Question: Tell me about yourself and your qualifications.
Answer: Certainly! Over the past three years, I've been working as a bookkeeper, where I've managed accounts payable and receivable, along with payroll oversight. I take pride in my ability to identify and resolve discrepancies, leading to substantial cost savings for my company. Recently, I earned my CPA degree, and I'm confident that my expertise in bookkeeping, coupled with my attention to detail, aligns well with the requirements of the public accountant role at your organization.

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
    return ChatOpenAI(api_key=os.getenv("API_KEY"), model="gpt-3.5-turbo-0125", temperature=0.2)


def create_conversation_chain(llm):
    return ConversationChain(
        memory=st.session_state.buffer_memory, prompt=chat_prompt_template, llm=llm, verbose=True)

# Ask a question


def ask_question():
    return st.chat_input("Ask a question", key="input")


def get_summarized_questions(url_chunks: List[str]):
    llm = initialize_openai_client()

    map_prompt = """
    You are helpful AI assistant that trains the user on personalized interview questions.
    The below context is from a Interview questions website. Please identify only intreview questions and its answers.

    % START OF CONTEXT
    {text}
    % END OF CONTEXT

    Your Response: """

    map_prompt_template = PromptTemplate(
        template=map_prompt, input_variables=["text"])

    combined_prompt = """
    Combine the context provide all the interview questions and answers based on the context.
    Do not make anything up, only use information provided in the context.

    % START OF CONTEXT
    {text}
    % END OF CONTEXT
    """

    combined_prompt_template = PromptTemplate(
        template=combined_prompt, input_variables=["text"])

    # Load summarization chain
    chain = load_summarize_chain(llm,
                                 chain_type="map_reduce",
                                 map_prompt=map_prompt_template,
                                 combine_prompt=combined_prompt_template,
                                 )

    output = chain({"input_documents": url_chunks})

    return output["output_text"]


# Generate questions


def generate_questions(url_chunks: List[str]):
    llm = initialize_openai_client()

    map_llm_template = """You are a helpful assistant who will train users on personalized interview questions. Your goal is to identify only interview questions and its answers in the following context:
        {context}.

        Provide questions if only relavant context is passed.

        Your response should be in this fashsion:
        1. Interviewer: Tell me about yourself and your qualifications.
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
    st.title("Career Coach")

    st.session_state["user_name"] = st.text_input(
        placeholder="User Name", label="User Name")

    pdf_files = upload_pdf_files()

    isUploaded = st.button("Summarize Resume")

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

    # Upload PDF files

    # Get index for
    if isUploaded and pdf_files is not None:
        if (st.session_state["user_name"] == ""):
            st.error("Please enter a user name")
            return

        with st.spinner("Summarizing your resume..."):
            time.sleep(4)

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
    else:
        st.error("Please upload a PDF file")

    # Summarize PDF
    if "summarized_pdf" in st.session_state:
        st.markdown("### Resume Summary")
        st.write(st.session_state["summarized_pdf"])

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
            url_chunks = url_chunks[:3]

            questions_and_answers = generate_questions(url_chunks)

            st.session_state["generated_questions"] = questions_and_answers

            q_and_a_docs = questions_text_splitter(
                questions_and_answers, urls[0], st.session_state["user_name"])
            st.write(q_and_a_docs)
            # url_index = get_url_index(q_and_a_docs)
        else:
            st.sidebar.error(
                "Please enter atleast one URL to generate questions")
    except Exception as e:
        st.error(f"Error processing URL")

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
                conversation_string = get_conversation_string()
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
