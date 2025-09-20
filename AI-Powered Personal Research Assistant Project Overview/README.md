# AI-Powered Personal Research Assistant

## Overview

The AI-Powered Personal Research Assistant is a sophisticated web application that enables users to upload documents and interact with their content through natural language queries. Built using modern AI technologies including Retrieval-Augmented Generation (RAG), vector embeddings, and large language models, this system creates an intelligent knowledge base from user-uploaded documents.

## Features

### Core Functionality
- **Multi-format Document Support**: Upload and process PDF, DOCX, DOC, and TXT files
- **Intelligent Text Processing**: Advanced chunking strategy with overlap to preserve context
- **Vector-based Search**: FAISS-powered similarity search for relevant content retrieval
- **Citation-backed Answers**: All responses include source citations with exact text passages
- **Real-time Chat Interface**: Interactive web-based chat with document knowledge base
- **Document Management**: Upload, view, and delete documents through intuitive interface

### Technical Highlights
- **Retrieval-Augmented Generation (RAG)**: Combines document retrieval with LLM generation
- **Vector Embeddings**: Uses OpenAI's text-embedding-ada-002 for semantic understanding
- **Scalable Architecture**: Modular design supporting easy extension and deployment
- **Modern Web Interface**: Responsive React frontend with professional UI components
- **RESTful API**: Well-documented backend API for all operations

## Architecture

### System Components

The application follows a client-server architecture with clear separation of concerns:

**Frontend (React)**
- Modern, responsive user interface built with React and Tailwind CSS
- Real-time chat interface with message history
- Document upload and management functionality
- Citation display with source highlighting

**Backend (Flask)**
- RESTful API handling document processing and chat requests
- Document parsing and text extraction
- Vector embedding generation and storage
- RAG pipeline implementation

**Data Layer**
- SQLite database for document metadata and chunks
- FAISS vector store for similarity search
- File system storage for uploaded documents

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Frontend | React, Tailwind CSS, shadcn/ui | User interface and interaction |
| Backend | Flask, Python | API server and business logic |
| Database | SQLite | Document metadata storage |
| Vector Store | FAISS | Similarity search and retrieval |
| LLM | OpenAI GPT-4 | Answer generation |
| Embeddings | OpenAI text-embedding-ada-002 | Semantic text representation |
| Document Processing | PyPDF2, python-docx | Text extraction from files |

## Installation and Setup

### Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- OpenAI API key

### Backend Setup

1. **Clone and navigate to backend directory**
   ```bash
   cd research-assistant-backend
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   ```

5. **Start the backend server**
   ```bash
   python src/main.py
   ```

The backend will be available at `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd research-assistant-frontend
   ```

2. **Install dependencies**
   ```bash
   pnpm install
   ```

3. **Start development server**
   ```bash
   pnpm run dev
   ```

The frontend will be available at `http://localhost:5173`

## Usage Guide

### Uploading Documents

1. **Access the Application**: Open your web browser and navigate to the frontend URL
2. **Select Document**: Click "Choose File" in the Document Library section
3. **Upload**: Select a supported file (PDF, DOCX, DOC, TXT) and click "Upload Document"
4. **Processing**: The system will extract text, create chunks, and generate embeddings
5. **Confirmation**: A success message will appear when processing is complete

### Chatting with Documents

1. **Enter Query**: Type your question in the chat input field
2. **Send Message**: Click the send button or press Enter
3. **Review Response**: The AI will provide an answer based on your documents
4. **Check Citations**: Source citations appear below each response with exact text passages
5. **Continue Conversation**: Ask follow-up questions to explore your documents further

### Managing Documents

- **View Documents**: All uploaded documents appear in the Document Library
- **Delete Documents**: Click the trash icon next to any document to remove it
- **Document Details**: View filename and upload date for each document

## API Documentation

### Endpoints

#### Upload Document
```http
POST /api/upload-document
Content-Type: multipart/form-data

Parameters:
- file: Document file (PDF, DOCX, DOC, TXT)

Response:
{
  "message": "Document uploaded and processed successfully",
  "document_id": "uuid-string",
  "filename": "document.pdf",
  "chunks_created": 15
}
```

#### Chat with Documents
```http
POST /api/chat
Content-Type: application/json

Body:
{
  "query": "What is the main topic of the document?",
  "document_ids": ["uuid1", "uuid2"] // Optional
}

Response:
{
  "answer": "The main topic is...",
  "citations": [
    {
      "document_id": "uuid",
      "filename": "document.pdf",
      "text": "Relevant passage...",
      "similarity_score": 0.85
    }
  ],
  "retrieved_chunks": 5
}
```

#### List Documents
```http
GET /api/documents

Response:
{
  "documents": [
    {
      "document_id": "uuid",
      "filename": "document.pdf",
      "upload_date": "2024-01-01T00:00:00",
      "file_type": "pdf"
    }
  ]
}
```

#### Delete Document
```http
DELETE /api/delete-document/{document_id}

Response:
{
  "message": "Document deleted successfully"
}
```

## Development

### Project Structure

```
research-assistant/
├── research-assistant-backend/
│   ├── src/
│   │   ├── models/
│   │   │   ├── document.py      # Database models
│   │   │   └── user.py
│   │   ├── routes/
│   │   │   ├── research_assistant.py  # API endpoints
│   │   │   └── user.py
│   │   ├── services/
│   │   │   ├── document_processor.py  # Text processing
│   │   │   └── rag_service.py         # RAG implementation
│   │   └── main.py              # Flask application
│   ├── requirements.txt
│   └── venv/
├── research-assistant-frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── ui/              # UI components
│   │   ├── App.jsx              # Main application
│   │   └── main.jsx
│   ├── package.json
│   └── node_modules/
└── README.md
```

### Key Classes and Functions

#### DocumentProcessor
Handles document text extraction and processing:
- `extract_text_from_file()`: Extracts text from various file formats
- `chunk_text()`: Splits text into overlapping chunks
- `generate_embedding()`: Creates vector embeddings using OpenAI

#### VectorStore
Manages vector storage and similarity search:
- `add_embeddings()`: Stores embeddings with metadata
- `search()`: Performs similarity search
- `save_to_file()` / `load_from_file()`: Persistence operations

#### RAGService
Implements the RAG pipeline:
- `chat_with_documents()`: Main chat functionality
- `_generate_answer_with_citations()`: LLM response generation
- `summarize_document()`: Document summarization

### Testing

The project includes comprehensive testing:

#### Integration Tests
```bash
# Run mock integration test (no OpenAI API required)
python test_integration_mock.py

# Run full integration test (requires OpenAI API)
python test_integration.py
```

#### API Testing
```bash
# Test document upload
curl -X POST -F "file=@test_document.txt" http://localhost:5000/api/upload-document

# Test chat functionality
curl -X POST -H "Content-Type: application/json" \
  -d '{"query": "What is this document about?"}' \
  http://localhost:5000/api/chat
```

## Deployment

### Production Considerations

1. **Environment Variables**: Set production OpenAI API key
2. **Database**: Consider PostgreSQL for production use
3. **Vector Store**: Evaluate Pinecone or Weaviate for scalability
4. **Security**: Implement authentication and rate limiting
5. **Monitoring**: Add logging and error tracking
6. **Performance**: Optimize embedding generation and search

### Docker Deployment (Future Enhancement)

```dockerfile
# Backend Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
EXPOSE 5000
CMD ["python", "src/main.py"]
```

## Challenges and Solutions

### Challenge 1: Context Preservation in Text Chunking
**Problem**: Maintaining semantic coherence when splitting documents into chunks.

**Solution**: Implemented overlapping chunks with 200-character overlap to ensure context continuity across boundaries. This approach prevents important information from being split inappropriately.

### Challenge 2: Citation Accuracy
**Problem**: Providing accurate source citations for generated answers.

**Solution**: Developed a citation system that tracks the exact text passages used in answer generation, including document ID, filename, and similarity scores for transparency.

### Challenge 3: Vector Search Performance
**Problem**: Efficient similarity search across large document collections.

**Solution**: Utilized FAISS with normalized embeddings and inner product similarity for fast, accurate retrieval. The system supports both exact and approximate search methods.

### Challenge 4: User Experience Design
**Problem**: Creating an intuitive interface for complex AI functionality.

**Solution**: Designed a clean, modern interface with clear visual separation between document management and chat functionality, real-time feedback, and comprehensive citation display.

## Future Enhancements

### Planned Features
1. **Multi-document Reasoning**: Compare and contrast information across multiple documents
2. **Advanced Summarization**: Generate executive summaries and key insights
3. **Export Functionality**: Save conversations and generate reports
4. **Collaborative Features**: Share knowledge bases with team members
5. **Advanced Search**: Filter by document type, date, or custom metadata

### Technical Improvements
1. **Caching Layer**: Redis for embedding and response caching
2. **Async Processing**: Background document processing for large files
3. **Advanced Chunking**: Semantic-aware chunking using NLP techniques
4. **Multi-modal Support**: Image and table extraction from documents
5. **Performance Monitoring**: Detailed analytics and usage tracking

## Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Submit a pull request with detailed description

### Code Standards
- Follow PEP 8 for Python code
- Use ESLint configuration for JavaScript
- Include docstrings for all functions
- Maintain test coverage above 80%

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

For questions, issues, or contributions, please:
1. Check existing GitHub issues
2. Create a new issue with detailed description
3. Include system information and error logs
4. Provide steps to reproduce any problems

---



*Empowering knowledge discovery through intelligent document interaction*

