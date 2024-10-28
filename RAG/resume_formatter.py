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

    prompt_template = os.getenv("RESUME_FORMAT_PROMPT")

    prompt = PromptTemplate(input_variables=["text"], template=prompt_template)

    llm_chain = LLMChain(llm=llm, prompt=prompt)

    formatted_resume = llm_chain.run({"text": text})

    return formatted_resume
