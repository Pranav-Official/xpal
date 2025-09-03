import os
import chromadb
from dotenv import load_dotenv
from chromadb import Documents, EmbeddingFunction, Embeddings
import google.generativeai as genai
from typing import List
import uuid


load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=google_api_key)


# Custom embedding function for Google Generative AI
class GoogleGenerativeAIEmbeddingFunction(EmbeddingFunction):
    def __init__(self, api_key: str, model_name: str = "models/embedding-001"):
        self.model_name = model_name
        genai.configure(api_key=api_key)
        self.model = genai.embed_content

    def __call__(self, input: Documents) -> Embeddings:
        # Convert single string to list if needed
        if isinstance(input, str):
            input = [input]

        # Generate embeddings
        embeddings = []
        for doc in input:
            response = genai.embed_content(model=self.model_name, content=doc)
            embeddings.append(response["embedding"])
        return embeddings


def simple_text_splitter(
    text: str, chunk_size: int = 600, chunk_overlap: int = 100
) -> List[str]:
    """
    Simple text splitter to break document into chunks.

    Args:
        text (str): The text to split
        chunk_size (int): Maximum size of each chunk
        chunk_overlap (int): Overlap between chunks

    Returns:
        List[str]: List of text chunks
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end >= len(text):
            # Last chunk
            chunks.append(text[start:])
            break
        else:
            # Find a good breaking point (period, newline, space)
            chunk = text[start:end]
            # Try to break at sentence end or newline
            last_period = chunk.rfind(".")
            last_newline = chunk.rfind("\n")
            last_space = chunk.rfind(" ")

            # Choose the best breaking point
            break_point = max(last_period, last_newline, last_space)
            if break_point > 0:
                chunk = text[start : start + break_point + 1]

            chunks.append(chunk)
            # Move start position with overlap
            if break_point > 0:
                start += break_point + 1 - chunk_overlap
            else:
                start += chunk_size - chunk_overlap

    return chunks


def embed_docs(
    doc_content: str,
    collection_name: str = "health_docs",
    persist_directory: str = "./chroma_langchain_db",
):
    """
    Embeds a given document content into a Chroma vector database.

    Args:
        doc_content (str): The text content of the document to embed.
        collection_name (str): The name of the collection in Chroma DB.
        persist_directory (str): The directory where the Chroma DB will be persisted.

    Returns:
        chromadb.Collection: The Chroma collection object.
    """
    client = chromadb.PersistentClient(path=persist_directory)

    embedding_function = GoogleGenerativeAIEmbeddingFunction(
        api_key=google_api_key, model_name="models/embedding-001"
    )

    collection = client.get_or_create_collection(
        name=collection_name, embedding_function=embedding_function
    )

    # Split document into chunks
    texts = simple_text_splitter(doc_content, chunk_size=600, chunk_overlap=100)

    # Generate unique IDs for each chunk
    ids = [str(uuid.uuid4()) for _ in range(len(texts))]

    # Add documents to collection
    collection.add(ids=ids, documents=texts)

    print("Documents embedded and persisted successfully.")
    return collection


def retrive_doc_embeddings(
    query: str,
    collection_name: str = "health_docs",
    persist_directory: str = "./chroma_langchain_db",
):
    """
    Retrieve document embeddings from Chroma database based on a query.

    Args:
        query (str): The query text to search for.
        collection_name (str): The name of the collection in Chroma DB.
        persist_directory (str): The directory where the Chroma DB is persisted.

    Returns:
        List[Dict]: List of retrieved documents with their content and metadata.
    """
    try:

        client = chromadb.PersistentClient(path=persist_directory)

        embedding_function = GoogleGenerativeAIEmbeddingFunction(
            api_key=google_api_key, model_name="models/embedding-001"
        )

        collection = client.get_collection(
            name=collection_name, embedding_function=embedding_function
        )

        print(f"Successfully loaded Chroma DB from {persist_directory}")
    except Exception as e:
        print(f"Error loading Chroma DB: {e}")
        return "Error loading from vector db"

    # Query the collection
    results = collection.query(query_texts=[query], n_results=5)

    if not results["ids"][0]:
        return "No relevant documents found for your query."

    retrieved_data = []
    for i in range(len(results["ids"][0])):
        retrieved_data.append(
            {
                "page_content": results["documents"][0][i],
                "metadata": (
                    results["metadatas"][0][i] if results["metadatas"][0] else {}
                ),
            }
        )

    return retrieved_data
