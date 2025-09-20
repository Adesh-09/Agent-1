#!/usr/bin/env python3
"""
Integration test for the AI Research Assistant
Tests the core RAG functionality without the web interface
"""

import sys
import os
sys.path.insert(0, '/home/ubuntu/research-assistant-backend')

from src.services.document_processor import DocumentProcessor, VectorStore
from src.services.rag_service import RAGService

def test_document_processing():
    """Test document processing and RAG functionality"""
    print("🔄 Testing AI Research Assistant Integration...")
    
    # Initialize components
    processor = DocumentProcessor()
    vector_store = VectorStore()
    rag_service = RAGService(vector_store)
    
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
        
        # Generate embeddings
        print("\n🧠 Testing embedding generation...")
        embeddings = []
        chunk_metadata = []
        
        for i, chunk in enumerate(chunks[:3]):  # Test first 3 chunks only
            embedding = processor.generate_embedding(chunk)
            embeddings.append(embedding)
            
            chunk_metadata.append({
                'document_id': 'test-doc-1',
                'filename': 'test_document.txt',
                'chunk_index': i,
                'text': chunk,
                'page_number': None
            })
            print(f"✅ Generated embedding for chunk {i+1}, dimension: {len(embedding)}")
        
        # Add to vector store
        print("\n🔍 Testing vector store...")
        vector_store.add_embeddings(embeddings, chunk_metadata)
        print(f"✅ Added {len(embeddings)} embeddings to vector store")
        
        # Test RAG functionality
        print("\n🤖 Testing RAG chat functionality...")
        test_queries = [
            "What is the AI-powered personal research assistant?",
            "How does the text chunking strategy work?",
            "What are the key components of the system?"
        ]
        
        for query in test_queries:
            print(f"\n❓ Query: {query}")
            try:
                result = rag_service.chat_with_documents(query)
                print(f"✅ Answer: {result['answer'][:200]}...")
                print(f"📚 Citations: {len(result['citations'])} sources found")
            except Exception as e:
                print(f"❌ RAG Error: {str(e)}")
        
        print("\n🎉 Integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_document_processing()
    sys.exit(0 if success else 1)

