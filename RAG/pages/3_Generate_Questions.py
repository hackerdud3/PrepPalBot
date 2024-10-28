import os
import streamlit as st
from typing import List
from url_loader_and_splitter import get_url_chunks
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents.stuff import create_stuff_documents_chain


def generate_questions_from_stuffed_docs(url_chunks: List[str]):
    llm = ChatOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini-2024-07-18",
        temperature=0.2,
    )

    prompt_template = """
    You are a helpful assistant tasked with training users on personalized interview questions. Your goal is to identify 10 interview questions and provide corresponding answers based on the context provided below, in a sequential manner.
    Provide questions only if the context is relevant to interviews.

    Your response should strictly follow this format:
    For example:
    1. Interviewer: Tell me about yourself and your qualifications?
    \nAnswer: Certainly! Over the past three years, I've been working as a bookkeeper, where I've managed accounts payable and receivable, along with payroll oversight. I take pride in my ability to identify and resolve discrepancies, leading to substantial cost savings for my company. Recently, I earned my CPA degree, and I'm confident that my expertise in bookkeeping, coupled with my attention to detail, aligns well with the requirements of the public accountant role at your organization.

    %CONTEXT
    {context}

    Interview questions and answers:
    """
    stuff_prompt = PromptTemplate.from_template(prompt_template)

    stuff_chain = create_stuff_documents_chain(llm=llm, prompt=stuff_prompt)

    return stuff_chain.stream({"context": url_chunks})


def main():
    st.title("🔗 Generate Questions")

    url = st.text_input("Careersite URL", placeholder="https://www.example.com")
    if "user_name" not in st.session_state:
        st.session_state["user_name"] = "Vinay"

    process_url = st.button("Generate Interview Questions")

    if "generated-questions" in st.session_state:
        st.write(st.session_state["generated_questions"])

    if process_url:
        if url is None:
            st.error("Please enter URL")
            return

        if st.session_state["user_name"] == "":
            st.error("Please enter username to continue")
            return

        url_chunks = get_url_chunks(url, st.session_state["user_name"])
        url_chunks = url_chunks[:10]

        with st.spinner("Generating Interview Questions..."):
            st.markdown("### Interview Questions and Answers from the website")
            questions_and_answers = st.write_stream(
                generate_questions_from_stuffed_docs(url_chunks)
            )
            st.session_state["generated_questions"] = questions_and_answers


if __name__ == "__main__":

    main()
