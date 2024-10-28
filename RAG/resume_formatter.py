import os
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain_core.output_parsers import StrOutputParser


def format_resume(text: str) -> str:
    llm = ChatOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini-2024-07-18",
        temperature=0,
    )

    prompt_template = os.getenv("RESUME_FORMAT_PROMPT")

    prompt = PromptTemplate(input_variables=["text"], template=prompt_template)

    chain = prompt | llm | StrOutputParser()

    formatted_resume = chain.invoke({"text": text})

    return formatted_resume
