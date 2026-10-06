import chromadb

from llama_index.core import (
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    Settings,
)

from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

from src.rag_src.config.rag_settings import rag_settings , BASE_DIR


def ingest_documents():

    # 1. Configure embedding model
    Settings.embed_model = HuggingFaceEmbedding(
        model_name=rag_settings.EMBEDDING_MODEL
    )

    # 2. Configure chunking
    Settings.text_splitter = SentenceSplitter(
        chunk_size=512,
        chunk_overlap=50
    )

    # 3. Load enterprise documents
    docs_path = BASE_DIR / rag_settings.DOCS_DIR

    documents = SimpleDirectoryReader(
        input_dir=str(docs_path),
        recursive=True,
        required_exts=[".md"]
    ).load_data()

    print(f"Loaded documents: {len(documents)}")

    # 4. Create persistent ChromaDB client
    chroma_db_path = BASE_DIR / rag_settings.CHROMA_DB_DIR

    chroma_client = chromadb.PersistentClient(
        path=str(chroma_db_path)
    )

    # 5. Create/get collection
    chroma_collection = chroma_client.get_or_create_collection(
        name=rag_settings.CHROMA_COLLECTION
    )

    # 6. Connect LlamaIndex to ChromaDB
    vector_store = ChromaVectorStore(
        chroma_collection=chroma_collection
    )

    storage_context = StorageContext.from_defaults(
        vector_store=vector_store
    )

    # 7. Create embeddings and store them
    VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        show_progress=True
    )

    print("Document ingestion completed successfully.")


if __name__ == "__main__":
    ingest_documents()