import re
import os
import streamlit as st
import nltk
import time
from nltk.corpus import stopwords
from langchain.docstore.document import Document
from rag_chain import parse_pdf
from resume_summarize_chain import load_summarize
from langchain_openai import ChatOpenAI


# Clean Resume file
def clean_resume(resume_text: str) -> str:
    # Download the stopwords list
    nltk.download("stopwords")
    stop_words = set(stopwords.words("english"))

    cleaned_resume = re.sub(r"\n+", " ", resume_text)

    # Tokenize the text into words
    words = re.findall(r"\b\w+\b|\.|\,|\-", cleaned_resume)

    # Remove stopwords
    cleaned_words = [word for word in words if word not in stop_words]
    cleaned_description = " ".join(cleaned_words)

    return cleaned_description


def stream_data(text: str):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.02)


def main():
    st.title("📝 Summarize Resume")

    llm = ChatOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini-2024-07-18",
        temperature=0.5,
    )

    # File uploader for the resume (PDF only)
    resume_pdf = st.file_uploader(
        label="Upload Resume", type="pdf", accept_multiple_files=False
    )

    # Store the uploaded resume in session state
    if resume_pdf:
        st.session_state["resume_pdf"] = resume_pdf
        st.session_state["summarized_resume"] = ""

    # Button to trigger resume summarization
    summarize = st.button(label="Summarize Resume")

    # Initialize session state for username if not present
    if "username" not in st.session_state:
        st.session_state["username"] = ""

    if summarize:
        st.session_state["summarized_resume"] = None

        has_error = False

        # Check if resume is uploaded
        if resume_pdf is None:
            st.error("Please upload resume")
            has_error = True

        # # Username validation
        # if st.session_state["username"] == "":
        #     st.error("Please enter username")
        #     has_error = True

        if has_error:
            return

        with st.spinner("Thinking..."):
            resume_text = parse_pdf(resume_pdf)
            cleaned_resume = clean_resume(resume_text)

        with st.spinner("Summarizing..."):
            summarized_pdf = load_summarize(cleaned_resume, llm)
            st.markdown("### Resume Summary")
            st.write_stream(stream_data(summarized_pdf))
            st.session_state["summarized_resume"] = summarized_pdf


if __name__ == "__main__":
    main()
