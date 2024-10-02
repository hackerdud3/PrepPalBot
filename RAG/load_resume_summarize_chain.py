from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from typing import List
from langchain.docstore.document import Document


def load_summarize(url_chunks: List[str], llm):

    llm = llm

    map_prompt = """
    The below context is from a user's resume. Please summarize all the themes in the resume.
    Write paragraphs for each theme and include all the necessary details. Do not make anything up, only use information provided in the context.

    % START OF CONTEXT
    {text}
    % END OF CONTEXT

    Your Response: """

    map_prompt_template = PromptTemplate(
        template=map_prompt, input_variables=["text"])

    combined_prompt = """
    Combine the context provide a 1-page concise summary of the user based on the context. Include all the necessary details, don't miss anything.
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

    output = chain.invoke({"input_documents": url_chunks})

    return output["output_text"]
