import requests
from bs4 import BeautifulSoup
from typing import List
import pymupdf # for pdf

import os

class TextHelper:
    def __init__(self):
        self.path = ""
       
    def load(self, path: str):
        self.path = path
        if path.startswith("http"):
            return self.load_html(path)
        elif path.endswith(".pdf"):
            return self.load_pdf_text(path)
        

    def load_html(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            return self.extract_titles_and_text(response.content)
        else:
            return None
        
    def extract_titles_and_text(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        titles_and_texts = []

        for i in range(1, 7):  # Loop through h1 to h6
            headers = soup.find_all(f'h{i}')
            for header in headers:
                title = header.get_text(strip=True)
                text = ''
                for sibling in header.next_siblings:
                    if sibling.name and sibling.name.startswith('h') and sibling.name != f'h{i}':
                        break
                    if sibling.name and sibling.name.startswith('h') and sibling.name == f'h{i}':
                        break
                    if sibling.name:
                        text += sibling.get_text(strip=True) + ' '
                text = text.replace("\n", " ")
                titles_and_texts.append((title, text.strip()))

        return titles_and_texts

    def load_pdf_text(self, pdf_path):
        # Open the PDF file
        
        document = pymupdf.open(pdf_path)   
        # Initialize an empty string for the text
        text = ""  
        # Iterate through each page of the PDF
        for page in document:
            # Extract text from the page and add it to the text string
            text += page.get_text() 
        # Close the document
        document.close()    
        # Return the extracted text
        return text



    def list_files(self):
        # Lists all files (not directories) in the current directory.
        print(os.getcwd())
        files = []
        for entry in os.listdir():
            if os.path.isfile(entry):
                files.append(entry)
        print(files)
        return files
    
class CharacterTextSplitter:
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        assert (
            chunk_size > chunk_overlap
        ), "Chunk size must be greater than chunk overlap"

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, text: str) -> List[str]:
        chunks = []
        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            chunks.append(text[i : i + self.chunk_size])
        return chunks

    def split_texts(self, texts: List[str]) -> List[str]:
        chunks = []
        for text in texts:
            chunks.extend(self.split(text))
        return chunks
    

if __name__ == "__main__":
    th = TextHelper()
    th.list_files()
    doc = th.load("Python4RAG/data/2205.13147v4.pdf")
    splitter = CharacterTextSplitter(chunk_size=800,chunk_overlap=200)
    chunks = splitter.split(doc)
    print(len(chunks))