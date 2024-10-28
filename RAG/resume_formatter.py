import os
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain


def format_resume(text: str) -> str:
    llm = ChatOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini-2024-07-18",
        temperature=0,
    )

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

    Please follow these guidelines and format very strictly:
    - Split the resume into above sections, using a ** question mark (?)** before section title and **colon (:)** after section title.
    - Within each section, separate individual entries using single line breaks.
    - Don't make section headings or anything bold, no additional formattings like bullet points, lines, or any special characters are needed.
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
    
    Here is the resume:
    <Resume>
    {text}

    """

    prompt = PromptTemplate(input_variables=["text"], template=prompt_template)

    llm_chain = LLMChain(llm=llm, prompt=prompt)

    formatted_resume = llm_chain.run({"text": text})

    return formatted_resume
