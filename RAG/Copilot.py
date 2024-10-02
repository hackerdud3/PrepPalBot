import os
import re
import time
import nltk
from nltk.corpus import stopwords
import streamlit as st
from typing import List
from PyPDF2 import PdfReader
from io import BytesIO
from dotenv import load_dotenv
from rag import parse_pdf
from mongoDBclient import client
from langchain_openai import ChatOpenAI
from rag import pinecone_vector_store
from streamlit_chat import message
from resume_formatter import format_resume
from langchain.docstore.document import Document
from load_resume_summarize_chain import load_summarize
from langchain.chains.llm import LLMChain
from langchain.embeddings import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
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
database = client[os.getenv("MONGODB_DATABASE")]
collection = database[os.getenv("MONGODB_RESUME_COLLECTION")]


# Initializing OPENAI client
def initialize_openai_client():
    return ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o-mini-2024-07-18", temperature=0.2)

# Initializing finetuned model
def initialize_finetuned_openai_client():
    return ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model=os.getenv("FINETUNED_MODEL"), temperature=0.2)

system_prompt_template = """
You are an intelligent Interview Prep chatbot designed to provide the best possible responses to interview questions based on the context provided, which includes the user’s resume, job description, and sample interview answers. Craft the best possible answer using only the provided information.You are interactive, guiding the user step by step through each question, helping them reflect on their own experiences, and offering tailored feedback to improve their responses.

Always refer to the provided resume and job description when crafting answers. 
Tailor responses to highlight relevant skills and experiences from the user's background. Train the user on how to answer questions effectively, providing suggestions and examples when necessary. 

Purpose:Provide the most accurate and relevant answers to interview questions based on the user's background and job requirements.
Make the session interactive by engaging the user, prompting them for details, and offering suggestions on how to improve their responses.

Interaction Flow:
Engage the User:Start by encouraging the user by saying something like "Hey there Let’s get you started with your interview prep. Here’s your first question".
Present each question one at a time and ask: How would you answer this?

Best Possible Answer:
Based on the user’s input, generate the best possible response using the STAR method for behavioral questions or other suitable frameworks for situational, technical, or opinion-based questions.
Ensure that the answers are specific, professional, and directly relevant to the job description and resume.

Guiding the User:
If the user's answer is incomplete or could be improved, suggest additional details: You might want to elaborate on the outcome of this action.
If they need help structuring their response, guide them: It’s helpful to frame your answer using the STAR method: What was the Situation, what Task were you responsible for, what Actions did you take, and what Results did you achieve?

Requesting More Information:
When the user's response lacks key details, ask follow-up questions: Can you provide more detail on the challenge you faced? or How did you measure success in this situation?
If no answer is provided, ask for specific details: Can you share a situation from your experience that relates to this?

Tailored Feedback and Suggestions:
After providing the best possible answer, give tailored suggestions based on the user’s input: This answer works well, but highlighting the impact of your work could strengthen it further.
Offer practical advice for improving the response, such as including metrics: Mentioning the percentage increase in efficiency after implementing this solution would be a great way to quantify your achievement.

Encouraging Reflection:
Encourage users to reflect on their answers and how they might improve: Does this feel like an accurate reflection of your experience? or Would you like to add any more context to this example?

Follow these guidelines for answering different types of interview questions:
Behavioral questions:    
- Use the STAR method: Situation (set the scene), Task (describe the challenge), Action (explain what you did), Result (share the outcome and lessons learned).   
- Use strong examples of strengths in action, matching them with the job requirements.   
- Be professional, honest, and authentic.   
- Quantify achievements and balance hard and soft skills.   
- When addressing weaknesses, present a recovery plan and show efforts to improve.

Situational questions:   
- Respond to hypothetical scenarios with practical approaches likely to occur on the job.   
- Focus on real, targeted challenges related to the position.

Opinion-based questions:   
- Provide a clear stance and defend it.   
- Showcase decision-making ability, industry insight, and a functional point of view.

Technical questions:   
- Offer clear and concise answers that demonstrate expertise.   
- If the question requires specific technical knowledge not provided in the context, advise the user to research the topic thoroughly before the interview.

General questions:   
- Keep answers brief and informative, directly addressing the question.

Competency-Based Questions:   
- Highlight Core Skills: These questions assess specific competencies like leadership, teamwork, or communication. Illustrate these skills with examples that showcase your ability to excel in key areas required for the role.   
- Relate to Role: Ensure that the competencies you highlight are directly relevant to the job description. Show how your strengths make you an ideal candidate for the position.

Motivational Questions:   
- Align with Company Values: Explain what motivates you in a way that aligns with the company’s values and mission.   
- Show Passion: Discuss why you are passionate about the role, the industry, or the company. This is your chance to convey enthusiasm and long-term interest.   
- Career Growth: Tie your motivation to your career goals, showing how the role fits into your professional development.

Conflict Resolution Questions:   
- Stay Objective: Describe a situation where you dealt with conflict in a professional setting. Focus on how you remained objective and addressed the issue constructively.   
- Emphasize Resolution: Highlight your conflict-resolution skills by explaining the steps you took to resolve the situation and what the outcome was. Showcase diplomacy, communication skills, and the ability to find common ground.


Cultural Fit Questions:   
- Reflect Company Culture: Tailor your responses to align with the company’s culture. Research the company's values and working style, and demonstrate how your personal and professional values are a match.   
- Highlight Collaboration: If teamwork and collaboration are emphasized, provide examples of how you’ve successfully worked in diverse teams and contributed to a positive work environment.

Leadership Questions:   
- Demonstrate Leadership Style: When asked about leadership, provide examples that showcase your leadership style, whether it's through leading a project, mentoring others, or facilitating teamwork.
- Adaptability: Show how you can adapt your leadership approach to different situations and team dynamics.

For all question types, follow this structure:
1) Briefly acknowledge the question
2) Provide a concise, relevant answer
3) Offer an example or elaboration if appropriate
4) Conclude with a statement that ties back to the job requirements

Additional guidelines:
- If a question is vague or could be interpreted in multiple ways, suggest asking for clarification before answering.
- After providing an answer, encourage the user to reflect on their own experiences and how they might apply the advice given.
- Be aware of and avoid potential biases in your responses. Ensure answers are inclusive and do not discriminate based on age, gender, race, or other protected characteristics.
- Always encourage honest, authentic responses. Advise against fabricating experiences or exaggerating accomplishments.
- For challenging questions about failures or weaknesses, advise on how to frame responses positively, focusing on growth and learning.
- Offer general interview etiquette advice, such as maintaining eye contact, using appropriate body language, and asking thoughtful questions about the company and role.

If you lack enough information to provide a specific answer, highlight what should be included to deliver the best response and offer general guidance instead."
"""

system_template_test = """
You are an intelligent Interview Prep copilot, designed to provide optimal responses to interview questions based on the user's resume, job description, and sample answers. Your role is to guide users through their responses interactively, helping them reflect on their experiences and offering tailored feedback for improvement.

Key Responsibilities:
- **Engagement**: Start by encouraging the user: "Hey there, Let’s get you started with your interview prep. Here’s your first question." Present questions one at a time and ask, "How would you answer this?"
- **Response Crafting**: Generate answers using the STAR method for behavioral questions or appropriate frameworks for other types. Ensure responses are specific, professional, and relevant to the user's background.

Guiding the User:
- Suggest improvements for incomplete answers: "Consider elaborating on the outcome."
- Help structure responses with the STAR method: "What was the Situation, Task, Actions, and Results?"

Requesting Information:
- Ask follow-up questions for more detail: "Can you provide an example from your experience?"
- If necessary, prompt for specific situations.

Tailored Feedback:
- After generating a response, provide suggestions to enhance it: "Highlighting the impact could strengthen your answer."
- Offer practical advice, such as quantifying achievements.

Encouraging Reflection:
- Prompt users to reflect: "Does this accurately reflect your experience?"

Guidelines for Answering Questions:
- **Behavioral**: Use the STAR method, highlight strengths, and quantify achievements.
- **Situational**: Offer practical responses to hypothetical scenarios.
- **Opinion-Based**: State a clear stance and defend it.
- **Technical**: Provide concise, knowledgeable answers, advising further research if needed.
- **General**: Keep answers informative and to the point.
- **Competency-Based**: Highlight core skills relevant to the role.
- **Motivational**: Align motivations with company values and demonstrate passion for the role.
- **Conflict Resolution**: Focus on objective handling of conflicts and constructive outcomes.
- **Cultural Fit**: Tailor responses to reflect the company's culture and emphasize collaboration.
- **Leadership**: Provide examples of your leadership style and adaptability.

For all types of questions:
1) Acknowledge the question.
2) Provide a concise, relevant answer.
3) Offer examples if appropriate.
4) Conclude with a tie to job requirements.

Additional Notes:
- Seek clarification befor answering for vague questions or qusetions that could be interpreted in multiple ways.
- After providing an answer, encourage users to reflect on their experiences and apply the advice.
- Avoid biases and promote inclusivity in responses. Ensure answers are inclusive and do not discriminate based on age, gender, race, or other protected characteristics.
- Encourage authentic answers and positive framing of weaknesses.
- Share general interview etiquette tips, like maintaining eye contact and body language.

If lacking information for a specific answer, highlight needed details and offer general guidance.

"""

system_msg_template = SystemMessagePromptTemplate.from_template(
    template=system_template_test, input_variables=["input"])

human_msg_template = HumanMessagePromptTemplate.from_template(
    template="{input}")

chat_prompt_template = ChatPromptTemplate.from_messages(
    [system_msg_template, human_msg_template, MessagesPlaceholder(variable_name="history")])

urls = []

output_type = ""


# Create conversation chain
def create_conversation_chain(finetuned_llm):
    return ConversationChain(
        memory=st.session_state.buffer_memory, prompt=chat_prompt_template, llm=finetuned_llm, verbose=True)


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


# Clean description
def clean_description(job_description: str) -> str:
    # Download the stopwords list
    nltk.download('stopwords')
    stop_words = set(stopwords.words('english'))

    cleaned_job_description = re.sub(r"\n+", ". ", job_description)
    
    # Tokenize the text into words
    words = re.findall(r'\b\w+\b|\.|\,', cleaned_job_description)

    # Remove stopwords
    cleaned_words = [word for word in words if word not in stop_words]
    cleaned_description = ' '.join(cleaned_words)

    return cleaned_description

# Find match using Pinecone
def find_match(query, resume_id):
    knowledge = PineconeVectorStore.from_existing_index(index_name="pdf-embeddings", 
                                                        namespace=resume_id, 
                                                        embedding=OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY")))
    retriever = knowledge.as_retriever(
        search_type = "similarity_score_threshold",
        search_kwargs={"k": 5, "score_threshold": 0.5}
    )
    docs = retriever.invoke(input=query, filter={"resumeid": resume_id})
    return docs

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
    # Title
    st.title("💬 Prep Pal")
    st.caption("🚀 A carreer chatbot powered by GPT-4o")
    
    job_description = st.text_area(label = "Job Description", value="", height=30, 
                                   max_chars=None, 
                                   key=None, 
                                   help=None, 
                                   on_change=None, 
                                   args=None, 
                                   kwargs=None, 
                                   placeholder="Job Description", 
                                   label_visibility="visible")
    
    cleaned_job_description = clean_description(job_description)

    INITIAL_MESSAGE = [{"role" : "assitant", "content": "Hey there, I am PrepPal, Let's prep for your interview"}]
    
    if "messages" not in st.session_state:
        st.session_state["messages"] = INITIAL_MESSAGE

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if "buffer_memory" not in st.session_state:
        st.session_state.buffer_memory = ConversationBufferWindowMemory(
            k=3, return_messages=True, memory_key='history')
    
    with st.sidebar:
        "[View the source code](https://github.com/hackerdud3/PrepPalBot)"
        "[![View GitHub source code](https://github.com/codespaces/badge.svg)](https://organic-train-6vxgw7v674jfrr4r.github.dev/)"
        
        st.session_state["user_name"] = st.text_input(
        placeholder="User Name", label="User Name")
        pdf_files = st.file_uploader(label="Upload Resume", type=["pdf"], accept_multiple_files=False)
        uploaded_resume = st.button("Upload Resume")
        parse_test = st.sidebar.button("Parse")

    # Chat model
    llm = initialize_openai_client()
    finetuned_llm = initialize_finetuned_openai_client()

    # Buffer memory
    if "buffer" not in st.session_state:
        st.session_state.buffer = ConversationBufferWindowMemory(
            k=0, return_messages=True)

    # Get instance of resume file
    if pdf_files is None:
        st.error("Please upload your resume to continue")

    elif uploaded_resume and pdf_files is not None:
        if (st.session_state["user_name"] == ""):
            st.error("Please enter a user name")
            return  
        # If a new file is uploaded then we need to reset the responses and requests
        st.session_state["messages"] = INITIAL_MESSAGE

        with st.spinner("Uploading your resume..."):
            time.sleep(5)
        resume_info = {
            "user_name": st.session_state["user_name"],
            "file_name": pdf_files.name,
        }

        inserted_data = collection.insert_one(resume_info)
        resume_id = inserted_data.inserted_id
        st.session_state["resume_id"] = str(resume_id)

        text = parse_pdf(pdf_files)
        st.session_state["resume_text"] = text
        formatted_resume = format_resume(text)
        st.session_state["formatted_resume"] = formatted_resume
        pinecone_vector_store(formatted_resume, str(resume_id))

        st.success("Resume uploaded successfully")

    if parse_test and "formatted_resume" in st.session_state:
        pinecone_vector_store(st.session_state["formatted_resume"], "123")


    # Conversation chain
    conversation_chain = create_conversation_chain(finetuned_llm)

    # Ask question
    question = ask_question()

    if question:
        if job_description == "":
            st.error("Please enter job description")
            return

        st.session_state.messages.append({"role": "user", "content": question})
        st.chat_message("user").write(question)

        with st.spinner("Typing..."):

            # Similarity search
            docs = find_match(question, st.session_state["resume_id"])

            # Extract docs content
            pdf_extract = ""
            for doc in docs:
                pdf_extract += doc.page_content

            # Formatting the prompt
            complete_prompt = f"\n\n-Job Description:\n{cleaned_job_description}\n\n-Resume:\n{st.session_state.resume_text}\n\n-User:\n{question}"
            response = conversation_chain.predict(
                input=complete_prompt)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.chat_message("assistant").write(response)

if __name__ == '__main__':

    main()
