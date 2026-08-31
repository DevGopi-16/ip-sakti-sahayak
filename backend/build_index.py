import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

INDEX_PATH = os.path.join(BASE_DIR, "faiss_index")

try:
    from backend.ingest import load_and_chunk_docs
    from backend.providers import get_embeddings
except ImportError:
    from ingest import load_and_chunk_docs
    from providers import get_embeddings

from langchain_community.vectorstores import FAISS


def build_vector_store():
    print("Loading and chunking legal acts...")
    chunks = load_and_chunk_docs()

    if not chunks:
        print("No document chunks created. Exiting.")
        return

    print("Initializing local HuggingFace embedding engine...")
    embeddings = get_embeddings()

    print(f"Embedding {len(chunks)} chunks locally (No API rate limits)...")
    vectorstore = FAISS.from_documents(chunks, embeddings)

    vectorstore.save_local(INDEX_PATH)
    print(f"FAISS vector store saved successfully at: {INDEX_PATH}")


if __name__ == "__main__":
    build_vector_store()