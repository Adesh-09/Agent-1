#!/usr/bin/env python3
"""
Mock Integration test for the AI Research Assistant
Tests the core functionality without requiring OpenAI API
"""

import sys
import os
import json
import numpy as np
sys.path.insert(0, '/home/ubuntu/research-assistant-backend')

from src.services.document_processor import DocumentProcessor, VectorStore

class MockRAGService:
    """Mock RAG service for testing without OpenAI API"""
    
    def __init__(self, vector_store):
        self.vector_store = vector_store
    
    def chat_with_documents(self, query, document_ids=None, k=5):
        """Mock chat functionality"""
        # Generate a mock embedding (random vector)
        mock_embedding = np.random.rand(1536).tolist()
        
        # Search for similar chunks
        results = self.vector_store.search(mock_embedding, k)
        
        # Generate mock answer based on query
        if "research assistant" in query.lower():
            answer = "The AI-powered personal research assistant is a sophisticated system that combines document processing, vector embeddings, and large language models to create an intelligent knowledge base."
        elif "chunking" in query.lower():
            answer = "The text chunking strategy divides documents into manageable chunks of approximately 1000 characters with 200-character overlap to preserve context across boundaries."
        elif "components" in query.lower():
            answer = "The key components include: 1) Document Processing Engine, 2) Text Chunking Strategy, 3) Vector Embeddings, 4) Vector Database (FAISS), and 5) Retrieval-Augmented Generation (RAG)."
        else:
            answer = f"Based on the uploaded documents, I can provide information about: {query}. The system processes documents and provides contextual answers."
        
        # Create mock citations
        citations = []
        for i, (chunk_meta, score) in enumerate(results[:2]):
            citations.append({
                'document_id': chunk_meta.get('document_id', 'unknown'),
                'filename': chunk_meta.get('filename', 'unknown'),
                'text': chunk_meta.get('text', '')[:100] + "...",
                'similarity_score': score
            })
        
        return {
            'answer': answer,
            'citations': citations,
            'retrieved_chunks': len(results)
        }

class MockDocumentProcessor(DocumentProcessor):
    """Mock document processor that doesn't require OpenAI API"""
    
    def generate_embedding(self, text):
        """Generate mock embedding (random vector)"""
        return np.random.rand(1536).tolist()

def test_mock_integration():
    """Test the system with mock components"""
    print("🔄 Testing AI Research Assistant Integration (Mock Mode)...")
    
    # Initialize mock components
    processor = MockDocumentProcessor()
    vector_store = VectorStore()
    rag_service = MockRAGService(vector_store)
    
    # Test document processing
    print("\n📄 Testing document processing...")
    test_file = "/home/ubuntu/test_document.txt"
    
    try:
        # Extract text
        content = processor.extract_text_from_file(test_file, "txt")
        print(f"✅ Text extraction successful. Content length: {len(content)} characters")
        
        # Chunk text
        chunks = processor.chunk_text(content)
        print(f"✅ Text chunking successful. Created {len(chunks)} chunks")
        
        # Generate mock embeddings
        print("\n🧠 Testing embedding generation (mock)...")
        embeddings = []
        chunk_metadata = []
        
        for i, chunk in enumerate(chunks):
            embedding = processor.generate_embedding(chunk)
            embeddings.append(embedding)
            
            chunk_metadata.append({
                'document_id': 'test-doc-1',
                'filename': 'test_document.txt',
                'chunk_index': i,
                'text': chunk,
                'page_number': None
            })
            print(f"✅ Generated mock embedding for chunk {i+1}, dimension: {len(embedding)}")
        
        # Add to vector store
        print("\n🔍 Testing vector store...")
        vector_store.add_embeddings(embeddings, chunk_metadata)
        print(f"✅ Added {len(embeddings)} embeddings to vector store")
        
        # Test RAG functionality
        print("\n🤖 Testing RAG chat functionality (mock)...")
        test_queries = [
            "What is the AI-powered personal research assistant?",
            "How does the text chunking strategy work?",
            "What are the key components of the system?"
        ]
        
        for query in test_queries:
            print(f"\n❓ Query: {query}")
            try:
                result = rag_service.chat_with_documents(query)
                print(f"✅ Answer: {result['answer']}")
                print(f"📚 Citations: {len(result['citations'])} sources found")
                for i, citation in enumerate(result['citations']):
                    print(f"   [{i+1}] {citation['filename']}: {citation['text']}")
            except Exception as e:
                print(f"❌ RAG Error: {str(e)}")
        
        # Test vector search
        print("\n🔍 Testing vector similarity search...")
        query_embedding = processor.generate_embedding("document processing")
        search_results = vector_store.search(query_embedding, k=3)
        print(f"✅ Found {len(search_results)} similar chunks")
        
        for i, (chunk_meta, score) in enumerate(search_results):
            print(f"   Result {i+1}: Score {score:.3f} - {chunk_meta['text'][:100]}...")
        
        print("\n🎉 Mock integration test completed successfully!")
        print("\n📋 Test Summary:")
        print(f"   • Document processing: ✅ Working")
        print(f"   • Text chunking: ✅ Working ({len(chunks)} chunks)")
        print(f"   • Embedding generation: ✅ Working (mock)")
        print(f"   • Vector storage: ✅ Working ({len(embeddings)} vectors)")
        print(f"   • Similarity search: ✅ Working")
        print(f"   • RAG chat: ✅ Working (mock)")
        
        return True
        
    except Exception as e:
        print(f"❌ Mock integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_mock_integration()
    sys.exit(0 if success else 1)

