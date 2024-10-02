import os
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain

def format_resume(text:str) -> str:
    llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o-mini-2024-07-18", temperature=0)

    prompt_template = """
    Your task is to analyze and parse the resume provided below. Identify and extract the following sections:
    - Personal Details
    - Skills (Technical and Soft)
    - Experience (Work and Internships)
    - Education (Degrees)
    - Certifications (if any)
    - Projects (Personal and Academic)
    - Awards or Accomplishments (if any)
    - Activities and Volunteering (if any)
    - Hobbies (if any)

    Here is the resume:
    Start of resume
    {text}
    End of resume

    Please follow these guidelines strictly:
    - Split the resume into these sections, using a ** question mark (?)** before the section title and **colon (:)** after the section title.
    - Within each section, separate individual entries using single line breaks.
    - Don't make section headings or anything bold, no additional formatting like bullet points or special characters are needed.
    - For "Skills", list them as comma-separated values.
    - Avoid excessive spacing and ensure content is concise.
    - Use a clean structure
    
    Example Format:
    +Education:
    Degree, University, GPA, Year
    
    +Experience:
    Job title, Company, Date
    Description of work experience
    
    +Projects:
    Project name
    Brief description
    """

    prompt = PromptTemplate(input_variables=["text"], template=prompt_template)

    llm_chain = LLMChain(llm=llm, prompt=prompt)

    formatted_resume = llm_chain.run({"text": text})
    
    return formatted_resume