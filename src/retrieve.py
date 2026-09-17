import json
import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

def build_vector_store(json_path="data/documentation.json"):
    if not os.path.exists(json_path):
        print(f"Waiting for layout file at: {json_path}")
        return None
    with open(json_path, "r") as f:
        documents = json.load(f)
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
    texts, metadatas = [], []
    for doc in documents:
        for chunk in splitter.split_text(doc["content"]):
            texts.append(chunk)
            metadatas.append({"doc_id": doc["id"], "title": doc["title"]})
            
    embeddings = HuggingFaceEmbeddings(model_name=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"))
    store = Chroma.from_texts(
        texts=texts, metadatas=metadatas, embedding=embeddings,
        persist_directory=os.getenv("CHROMA_PATH", "./storage/chroma")
    )
    store.persist()
    return store

def query_vector_store(query_text, k=2):
    # This is the function api.py was looking for
    embeddings = HuggingFaceEmbeddings(model_name=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"))
    store = Chroma(
        persist_directory=os.getenv("CHROMA_PATH", "./storage/chroma"), 
        embedding_function=embeddings
    )
    return store.similarity_search(query_text, k=k)
