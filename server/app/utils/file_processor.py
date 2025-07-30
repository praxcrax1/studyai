from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import requests
import tempfile

def process_pdf(file_path: str, chunk_size: int=1000, chunk_overlap: int=200) -> list:
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return splitter.split_text(text)

def download_pdf(url: str) -> str:
    response = requests.get(url)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(response.content)
        return tmp_file.name