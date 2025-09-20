import os
import uuid
import PyPDF2
import docx
from typing import List, Tuple
import openai
import numpy as np
import faiss
import json

class DocumentProcessor:
    def __init__(self):
        self.openai_client = openai.OpenAI()
        self.chunk_size = 1000
        self.chunk_overlap = 200
        
    def extract_text_from_file(self, file_path: str, file_type: str) -> str:
        """Extract text content from uploaded file"""
        try:
            if file_type.lower() == 'pdf':
                return self._extract_from_pdf(file_path)
            elif file_type.lower() in ['docx', 'doc']:
                return self._extract_from_docx(file_path)
            elif file_type.lower() == 'txt':
                return self._extract_from_txt(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        except Exception as e:
            raise Exception(f"Error extracting text from {file_type} file: {str(e)}")
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    
    def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # If we're not at the end, try to break at a sentence or word boundary
            if end < len(text):
                # Look for sentence boundary
                sentence_end = text.rfind('.', start, end)
                if sentence_end > start:
                    end = sentence_end + 1
                else:
                    # Look for word boundary
                    word_end = text.rfind(' ', start, end)
                    if word_end > start:
                        end = word_end
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - self.chunk_overlap
            if start >= len(text):
                break
                
        return chunks
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI"""
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Error generating embedding: {str(e)}")
    
    def generate_document_id(self) -> str:
        """Generate unique document ID"""
        return str(uuid.uuid4())


class VectorStore:
    def __init__(self, dimension: int = 1536):
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        self.chunk_metadata = []  # Store chunk metadata
        
    def add_embeddings(self, embeddings: List[List[float]], metadata: List[dict]):
        """Add embeddings to the vector store"""
        embeddings_array = np.array(embeddings, dtype=np.float32)
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings_array)
        
        self.index.add(embeddings_array)
        self.chunk_metadata.extend(metadata)
    
    def search(self, query_embedding: List[float], k: int = 5) -> List[Tuple[dict, float]]:
        """Search for similar chunks"""
        query_array = np.array([query_embedding], dtype=np.float32)
        faiss.normalize_L2(query_array)
        
        scores, indices = self.index.search(query_array, k)
        
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.chunk_metadata):
                results.append((self.chunk_metadata[idx], float(score)))
        
        return results
    
    def save_to_file(self, filepath: str):
        """Save vector store to file"""
        faiss.write_index(self.index, f"{filepath}.index")
        with open(f"{filepath}.metadata", 'w') as f:
            json.dump(self.chunk_metadata, f)
    
    def load_from_file(self, filepath: str):
        """Load vector store from file"""
        if os.path.exists(f"{filepath}.index") and os.path.exists(f"{filepath}.metadata"):
            self.index = faiss.read_index(f"{filepath}.index")
            with open(f"{filepath}.metadata", 'r') as f:
                self.chunk_metadata = json.load(f)

