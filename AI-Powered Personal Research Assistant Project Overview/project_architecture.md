
# Project Architecture and Tech Stack

## 1. Backend Framework
- **Choice:** FastAPI
- **Reasoning:** Modern, fast (built on Starlette), asynchronous support out-of-the-box, automatic interactive API documentation (Swagger UI/ReDoc). Better suited for building robust APIs compared to Flask for this type of project.

## 2. LLM
- **Choice:** OpenAI GPT-4 (initially, for ease of integration and performance)
- **Reasoning:** High performance and widely used. Will consider LLaMA 2 or Mistral for self-hosting options later if resource constraints or privacy concerns arise.

## 3. Embeddings and Search (Vector Database)
- **Choice:** FAISS (for local development and initial prototyping)
- **Reasoning:** Efficient similarity search for dense vectors, easy to integrate locally. This allows for rapid development and testing without external dependencies. For future scalability, Weaviate or Pinecone would be considered.

## 4. Frontend
- **Choice:** Streamlit (for rapid prototyping and web demo)
- **Reasoning:** Quick and easy to build interactive web applications with Python. Ideal for showcasing the project's functionality quickly. React would be a more robust choice for a production-ready application, but Streamlit serves the portfolio-worthy goal well for a demo.

## 5. Overall Architecture
- User uploads documents via the Streamlit frontend.
- Frontend sends documents to the FastAPI backend.
- FastAPI backend processes documents:
    - Parses content.
    - Chunks text.
    - Generates embeddings using an embedding model (e.g., OpenAI embeddings).
    - Stores embeddings and document metadata in FAISS (vector database).
- User sends natural language queries to the FastAPI backend.
- FastAPI backend performs RAG:
    - Generates embedding for the query.
    - Searches FAISS for relevant document chunks.
    - Constructs a prompt with the query and retrieved chunks.
    - Sends prompt to the LLM (GPT-4).
    - LLM generates a response.
    - Backend identifies and extracts citations from the retrieved chunks.
- FastAPI backend sends the LLM response and citations back to the Streamlit frontend.
- Streamlit frontend displays the response and citations to the user.

