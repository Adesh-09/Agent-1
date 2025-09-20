import openai
from typing import List, Dict, Any
from src.services.document_processor import VectorStore

class RAGService:
    def __init__(self, vector_store: VectorStore):
        self.openai_client = openai.OpenAI()
        self.vector_store = vector_store
        
    def chat_with_documents(self, query: str, document_ids: List[str] = None, k: int = 5) -> Dict[str, Any]:
        """
        Chat with documents using RAG approach
        
        Args:
            query: User's natural language question
            document_ids: Optional list of specific document IDs to search in
            k: Number of relevant chunks to retrieve
            
        Returns:
            Dictionary containing answer and citations
        """
        try:
            # Generate embedding for the query
            query_embedding = self._generate_query_embedding(query)
            
            # Retrieve relevant chunks
            relevant_chunks = self.vector_store.search(query_embedding, k)
            
            # Filter by document IDs if specified
            if document_ids:
                relevant_chunks = [
                    (chunk, score) for chunk, score in relevant_chunks
                    if chunk.get('document_id') in document_ids
                ]
            
            # Generate answer using retrieved context
            answer, citations = self._generate_answer_with_citations(query, relevant_chunks)
            
            return {
                'answer': answer,
                'citations': citations,
                'retrieved_chunks': len(relevant_chunks)
            }
            
        except Exception as e:
            raise Exception(f"Error in RAG chat: {str(e)}")
    
    def _generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for user query"""
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=query
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Error generating query embedding: {str(e)}")
    
    def _generate_answer_with_citations(self, query: str, relevant_chunks: List[tuple]) -> tuple:
        """
        Generate answer using LLM with retrieved context and extract citations
        
        Args:
            query: User's question
            relevant_chunks: List of (chunk_metadata, similarity_score) tuples
            
        Returns:
            Tuple of (answer, citations)
        """
        if not relevant_chunks:
            return "I couldn't find relevant information in the uploaded documents to answer your question.", []
        
        # Prepare context from retrieved chunks
        context_parts = []
        citations = []
        
        for i, (chunk_metadata, score) in enumerate(relevant_chunks):
            chunk_text = chunk_metadata.get('text', '')
            document_id = chunk_metadata.get('document_id', '')
            page_number = chunk_metadata.get('page_number')
            filename = chunk_metadata.get('filename', 'Unknown')
            
            # Add to context with reference number
            context_parts.append(f"[{i+1}] {chunk_text}")
            
            # Prepare citation
            citation = {
                'document_id': document_id,
                'filename': filename,
                'text': chunk_text[:200] + "..." if len(chunk_text) > 200 else chunk_text,
                'similarity_score': score
            }
            
            if page_number is not None:
                citation['page_number'] = page_number
                
            citations.append(citation)
        
        context = "\n\n".join(context_parts)
        
        # Create prompt for LLM
        system_prompt = """You are a helpful research assistant. Answer the user's question based on the provided context from their uploaded documents. 

Important guidelines:
1. Only use information from the provided context
2. When referencing information, use the reference numbers [1], [2], etc. that correspond to the context sources
3. If the context doesn't contain enough information to answer the question, say so clearly
4. Be precise and cite your sources using the reference numbers
5. Provide a comprehensive answer when possible"""

        user_prompt = f"""Context from uploaded documents:
{context}

Question: {query}

Please answer the question based on the provided context, using reference numbers [1], [2], etc. when citing sources."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content
            return answer, citations
            
        except Exception as e:
            raise Exception(f"Error generating LLM response: {str(e)}")
    
    def summarize_document(self, document_content: str, max_bullets: int = 5) -> str:
        """
        Generate a summary of a document
        
        Args:
            document_content: Full text content of the document
            max_bullets: Maximum number of bullet points in summary
            
        Returns:
            Summary string
        """
        try:
            prompt = f"""Please provide a concise summary of the following document in {max_bullets} key bullet points:

{document_content[:4000]}  # Limit content to avoid token limits

Focus on the main ideas, key findings, and important conclusions."""

            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates concise, informative summaries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Error generating summary: {str(e)}")

