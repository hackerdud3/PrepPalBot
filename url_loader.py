from langchain_community.document_loaders import UnstructuredHTMLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_data_from_urls(urls: List[str]):
    loader = UnstructuredHTMLLoader(urls=urls)
    data = loader.load()
    return data


def url_splitter(data: List[str]):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, separators=[
                                              "\n\n", "\n", ".", "!", "?", ",", " ", ""], chunk_overlap=10)
    chunks = splitter.split_documents(data)
    return chunks
