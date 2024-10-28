import os
import re
import time
import nltk
import streamlit as st
from nltk.corpus import stopwords
from dotenv import load_dotenv
from rag_chain import parse_pdf, pinecone_vector_store
from mongodb_client import client
from langchain_openai import ChatOpenAI
from resume_formatter import format_resume
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.chains.llm import LLMChain
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
)
from langchain_core.output_parsers import StrOutputParser

try:
    stopwords.words("english")
except LookupError:
    nltk.download("stopwords")
    
load_dotenv()

# MongoDB database and collection
database = client[os.getenv("MONGODB_DATABASE")]
collection = database[os.getenv("MONGODB_RESUME_COLLECTION")]


# Initializing OpenAI chat model
def initialize_openai_client():
    return ChatOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini-2024-07-18",
        temperature=0.5,
    )


# Initializing OpenAI finetuned chat model
def initialize_finetuned_openai_client():
    return ChatOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        model=os.getenv("FINETUNED_MODEL"),
        temperature=1,
        streaming=True,
    )


# Clean the job description
def clean_description(text: str) -> str:
    """
    Cleans the job description by removing stopwords and excess newlines.

    Args:
        job_description (str): The raw job description text.

    Returns:
        str: The cleaned job description.
    """
    # Load English stopwords
    stop_words = set(stopwords.words("english"))
    # Remove newlines and extra spaces
    cleaned_job_description = re.sub(r"\n+", " ", text)
    # Tokenize the text into words, keeping punctuation
    words = re.findall(r"\b\w+\b|[.,%-]", cleaned_job_description)
    # Remove stopwords
    cleaned_words = [word for word in words if word.lower() not in stop_words]
    # Join cleaned words into a sentence
    return " ".join(cleaned_words)


# Clean the job description
def clean_resume(text: str) -> str:
    """
    Cleans the resume by removing excess newlines.

    Args:
        job_description (str): The raw job description text.

    Returns:
        str: The cleaned job description.
    """
    # Remove newlines and extra spaces
    cleaned_resume = re.sub(r"\n+", " ", text)
    return cleaned_resume


# Get chat history from buffer window
def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    """
    This function take session id. If that session id is not in session store
    then creates a session id. Creates a buffer window memory and
    stores last k messages in the memory.

    Args:
        session_id (str): Current session id as a thread

    Return:
        InMemoryChatMessageHistory: Stores messages in a memory list like this `messages: list[BaseMessage] = list`.
    """
    if session_id not in st.session_state["store"]:
        st.session_state["store"][session_id] = InMemoryChatMessageHistory()
    else:
        memory = ConversationBufferWindowMemory(
            chat_memory=st.session_state["store"][session_id], k=5, return_messages=True
        )
        key = memory.memory_variables[0]
        messages = memory.load_memory_variables({})[key]
        st.session_state["store"][session_id] = InMemoryChatMessageHistory(
            messages=messages
        )
    return st.session_state["store"][session_id]


# Find match using Pinecone
def find_match(question: str, resume_id: str) -> list[dict]:
    """
    This function takes `question` and `resumeid`,
    leverages vector similiarity search using vector index
    and returns k relevant chunks from vector database based
    on threshold score.

    Args:
        question (str): The question or query to match against the resume chunks.
        resume_id (str): The ID of the resume to search within the vector database.

    Returns:
        List[dict]: A list of k relevant resume chunks, each represented as a dictionary
        containing the chunk content and its similarity score. The list is sorted by
        relevance, with the highest scoring chunks first.

    Example:
        relevant_chunks = find_match("What are your strengths?", 123)
        print(relevant_chunks)

    """
    knowledge = PineconeVectorStore.from_existing_index(
        index_name="pdf-embeddings",
        namespace=resume_id,
        embedding=OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY")),
    )
    retriever = knowledge.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 5, "score_threshold": 0.5},
    )
    docs = retriever.invoke(input=question, filter={"resumeid": resume_id})
    return docs


def get_response(question: str, cleaned_job_description: str):
    # System message template
    system_msg_template = SystemMessagePromptTemplate.from_template(
        template=os.getenv("SYSTEM_PROMPT")
    )

    # Human message template
    human_msg_template = HumanMessagePromptTemplate.from_template(template="{input}")

    # Chat prompt
    prompt = ChatPromptTemplate.from_messages(
        [
            MessagesPlaceholder(variable_name="history"),
            system_msg_template,
            human_msg_template,
        ]
    )
    llm = initialize_finetuned_openai_client()
    # LLM chain
    chain = prompt = prompt | llm | StrOutputParser()
    # chain = LLMChain(prompt=chat_prompt, llm=initialize_finetuned_openai_client)
    chain_with_message_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )

    inputs = {
        "input": question,
        "job_description": cleaned_job_description,
        "resume": st.session_state.resume_text,
    }

    return chain_with_message_history.stream(
        inputs,
        {"configurable": {"session_id": "1"}},
    )


def main():
    # Create an in memory store for chat history
    if "store" not in st.session_state:
        st.session_state["store"] = {}

    # Initial message
    INITIAL_MESSAGE = [
        {
            "role": "assitant",
            "content": "Hey there, I am PrepPal, Let's prep for your interview",
        }
    ]

    with st.sidebar:
        "[View the source code](https://github.com/hackerdud3/PrepPalBot)"
        "[![View GitHub source code](https://github.com/codespaces/badge.svg)](https://organic-train-6vxgw7v674jfrr4r.github.dev/)"

        st.session_state["user_name"] = st.text_input(
            placeholder="User Name", label="User Name"
        )
        pdf_files = st.file_uploader(
            label="Upload Resume", type=["pdf"], accept_multiple_files=False
        )
        uploaded_resume = st.button("Upload Resume")

        if uploaded_resume and pdf_files is not None:
            if st.session_state["user_name"] == "":
                st.info("Please enter your username to continue")
                st.stop()
                return

            st.session_state["messages"] = INITIAL_MESSAGE
            with st.spinner("Uploading your resume to the database..."):
                text = parse_pdf(pdf_files)  # Parse resume text
                st.session_state["resume_text"] = clean_resume(text)
                formatted_resume = format_resume(text)  # Format resume using LLM
                st.session_state["formatted_resume"] = (
                    formatted_resume  # Store formatted resume
                )
                # Resume metadata
                resume_info = {
                    "user_name": st.session_state["user_name"],
                    "file_name": pdf_files.name,
                }
                # Insert resume data into MongoDB
                inserted_data = collection.insert_one(resume_info)
                resume_id = inserted_data.inserted_id  # Resume Id
                st.session_state["resume_id"] = str(resume_id)
                pinecone_vector_store(
                    formatted_resume, str(resume_id)
                )  # Store it in vectore database
                st.sidebar.success("Resume uploaded successfully")

    # Title
    st.title("💬 Prep Pal")
    st.caption("🚀 A carreer chatbot powered by GPT-4o")
    # Input for job description
    job_description = st.text_area(
        label="Job Description",
        value="",
        height=30,
        max_chars=None,
        key=None,
        help=None,
        on_change=None,
        args=None,
        kwargs=None,
        placeholder="Job Description",
        label_visibility="visible",
    )
    # Cleaned job description
    cleaned_job_description = clean_description(job_description)

    if "messages" not in st.session_state:
        st.session_state["messages"] = INITIAL_MESSAGE
    # Write AI and Human conversation
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # Question Answering
    if question := st.chat_input("Ask a question", key="input"):
        if st.session_state["user_name"] == "":
            st.info("Please add your username to continue")
            st.stop()
        if pdf_files is None:
            st.info("Please upload resume")
            st.stop()
        if "resume_id" not in st.session_state:
            st.info("Please click upload resume")
            st.stop()
        if job_description == "":
            st.info("Please enter job description")
            st.stop()

        st.session_state.messages.append({"role": "user", "content": question})
        st.chat_message("user").write(question)
        with st.chat_message("assistant"):
            response_text = st.write_stream(
                get_response(question, cleaned_job_description)
            )
        # Add the complete response text to session messages after streaming
        st.session_state.messages.append(
            {"role": "assistant", "content": response_text}
        )


if __name__ == "__main__":
    main()
