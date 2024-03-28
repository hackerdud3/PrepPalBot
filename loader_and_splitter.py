from langchain_community.document_loaders import UnstructuredHTMLLoader


def load_data_from_urls(urls: List[str]):
    loader = UnstructuredHTMLLoader(urls=urls)
    data = loader.load()
    return data
