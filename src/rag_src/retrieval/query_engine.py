import chromadb

from llama_index.core import VectorStoreIndex, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
from llama_index.vector_stores.chroma import ChromaVectorStore

from src.rag_src.config.rag_settings import rag_settings, BASE_DIR
from src.common.logging_config import get_logger


logger = get_logger("rag")


# =========================================================
# GLOBAL CACHE
# =========================================================
# None initially.
# After first initialization, the same query engine is reused.

_query_engine = None


# =========================================================
# 1. CREATE / GET QUERY ENGINE
# =========================================================

def get_query_engine():

    global _query_engine

    # -----------------------------------------------------
    # Reuse already initialized query engine
    # -----------------------------------------------------

    if _query_engine is not None:

        logger.info("Reusing cached RAG query engine")

        return _query_engine

    # -----------------------------------------------------
    # First-time initialization
    # -----------------------------------------------------

    logger.info("Initializing RAG query engine")

    # Configure embedding model
    logger.info(
        "Loading embedding model: %s",
        rag_settings.EMBEDDING_MODEL
    )

    Settings.embed_model = HuggingFaceEmbedding(
        model_name=rag_settings.EMBEDDING_MODEL,
        show_progress_bar=False
    )

    logger.info("Embedding model loaded successfully")

    # Configure Groq LLM
    Settings.llm = Groq(
        model=rag_settings.GROQ_MODEL,
        api_key=rag_settings.GROQ_API_KEY
    )

    logger.info(
        "Groq LLM configured: %s",
        rag_settings.GROQ_MODEL
    )

    # -----------------------------------------------------
    # Connect to persistent ChromaDB
    # -----------------------------------------------------

    chroma_db_path = BASE_DIR / rag_settings.CHROMA_DB_DIR

    logger.info(
        "Connecting to ChromaDB: %s",
        chroma_db_path
    )

    chroma_client = chromadb.PersistentClient(
        path=str(chroma_db_path)
    )

    logger.info(
        "Collections: %s",
        chroma_client.list_collections()
    )

    # Get existing collection
    chroma_collection = chroma_client.get_collection(
        name=rag_settings.CHROMA_COLLECTION
    )

    # Connect ChromaDB to LlamaIndex
    vector_store = ChromaVectorStore(
        chroma_collection=chroma_collection
    )

    # Rebuild LlamaIndex interface from stored vectors
    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store
    )

    # Create query engine
    _query_engine = index.as_query_engine(
        similarity_top_k=3
    )

    logger.info("RAG query engine initialized successfully")

    return _query_engine


# =========================================================
# 2. RAG QUERY
# =========================================================

def rag_query(query: str) -> dict:

    logger.info("Received RAG query: %s", query)

    query_engine = get_query_engine()

    # =====================================================
    # STEP 1: Retrieve ONCE
    # =====================================================

    retriever = query_engine.retriever

    retrieved_nodes = retriever.retrieve(query)

    logger.info(
        "Retrieved %s nodes from vector store",
        len(retrieved_nodes)
    )

    # =====================================================
    # STEP 2: Apply similarity threshold
    # =====================================================

    relevant_nodes = []

    for node in retrieved_nodes:

        file_name = node.node.metadata.get(
            "file_name",
            "unknown"
        )

        score = node.score

        logger.info(
            "Retrieved file=%s | score=%s",
            file_name,
            score
        )

        # Handle missing score
        if score is None:

            logger.warning(
                "REJECTED file=%s | score=None",
                file_name
            )

            continue

        # Accept node
        if score >= rag_settings.SIMILARITY_THRESHOLD:

            relevant_nodes.append(node)

            logger.info(
                "ACCEPTED file=%s | score=%.4f | threshold=%.2f",
                file_name,
                score,
                rag_settings.SIMILARITY_THRESHOLD
            )

        # Reject node
        else:

            logger.info(
                "REJECTED file=%s | score=%.4f | threshold=%.2f",
                file_name,
                score,
                rag_settings.SIMILARITY_THRESHOLD
            )

    # =====================================================
    # STEP 3: Stop if no relevant knowledge
    # =====================================================

    if not relevant_nodes:

        logger.warning(
            "No relevant documents found for query: %s",
            query
        )

        return {
            "answer": (
                "I couldn't find sufficient information "
                "in the knowledge base."
            ),
            "source_files": [],
            "grounded": False
        }

    # =====================================================
    # STEP 4: Build context from SAME retrieved nodes
    # =====================================================

    context_parts = []

    for node in relevant_nodes:

        context_parts.append(
            node.node.get_content()
        )

    context = "\n\n".join(context_parts)

    logger.info(
        "Built context using %s relevant nodes",
        len(relevant_nodes)
    )

    # =====================================================
    # STEP 5: Create grounded prompt
    # =====================================================

    prompt = f"""
You are an enterprise IT incident support assistant.

Answer the user's question using ONLY the provided
knowledge-base context.

Do not use outside knowledge.
Do not invent information.

If the context is insufficient, say:
"I couldn't find sufficient information in the knowledge base."

KNOWLEDGE BASE CONTEXT:
{context}

USER QUESTION:
{query}

ANSWER:
"""

    # =====================================================
    # STEP 6: Call Groq directly
    # NO SECOND RETRIEVAL
    # =====================================================

    logger.info("Sending grounded context to Groq LLM")

    response = Settings.llm.complete(prompt)

    logger.info("Groq response generated successfully")

    # =====================================================
    # STEP 7: Extract source filenames
    # =====================================================

    relevant_source_files = set()

    for node in relevant_nodes:

        file_name = node.node.metadata.get("file_name")

        if file_name:
            relevant_source_files.add(file_name)

    logger.info(
        "Sources used: %s",
        list(relevant_source_files)
    )

    # =====================================================
    # STEP 8: Return result
    # =====================================================

    return {
        "answer": response.text,
        "source_files": list(relevant_source_files),
        "grounded": True
    }