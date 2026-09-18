import json
import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

def build_vector_store(json_path="data/documentation.json"):
    if not os.path.exists(json_path):
        print(f"Waiting for collection data asset layout file at: {json_path}")
        return None
        
    with open(json_path, "r") as f:
        documents = json.load(f)
    
    # Key Failed Assumption Adjustment: Lower chunk to 500/100 to preserve listed sequences
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
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
    print(f"Successfully processed and stored {len(texts)} dense passages in Chroma DB.")
    return store

def query_vector_store(query_text, k=2):
    """Queries Chroma vector store returning matching passages accompanied by metadata."""
    embeddings = HuggingFaceEmbeddings(model_name=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"))
    if not os.path.exists(os.getenv("CHROMA_PATH", "./storage/chroma")):
        return []
    store = Chroma(
        persist_directory=os.getenv("CHROMA_PATH", "./storage/chroma"), 
        embedding_function=embeddings
    )
    return store.similarity_search(query_text, k=k)
