import os
import tempfile
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from src.models.document import Document, DocumentChunk, db
from src.services.document_processor import DocumentProcessor, VectorStore
from src.services.rag_service import RAGService

research_bp = Blueprint('research', __name__)

# Global instances (will be initialized in main.py)
document_processor = DocumentProcessor()
vector_store = VectorStore()
rag_service = RAGService(vector_store)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc'}
UPLOAD_FOLDER = 'uploads'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_folder():
    """Ensure upload folder exists"""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

@research_bp.route('/upload-document', methods=['POST'])
def upload_document():
    """Upload and process a document"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not supported. Supported types: txt, pdf, docx, doc'}), 400
        
        ensure_upload_folder()
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        
        # Create temporary file path
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as temp_file:
            file.save(temp_file.name)
            temp_file_path = temp_file.name
        
        try:
            # Extract text from file
            content = document_processor.extract_text_from_file(temp_file_path, file_extension)
            
            # Generate document ID
            document_id = document_processor.generate_document_id()
            
            # Save document to database
            document = Document(
                document_id=document_id,
                filename=filename,
                content=content,
                file_type=file_extension
            )
            db.session.add(document)
            
            # Chunk the text
            chunks = document_processor.chunk_text(content)
            
            # Generate embeddings and save chunks
            embeddings = []
            chunk_metadata = []
            
            for i, chunk_text in enumerate(chunks):
                # Generate embedding
                embedding = document_processor.generate_embedding(chunk_text)
                
                # Save chunk to database
                chunk = DocumentChunk(
                    document_id=document_id,
                    chunk_index=i,
                    text=chunk_text,
                    page_number=None  # Could be enhanced to track page numbers
                )
                chunk.set_embedding(embedding)
                db.session.add(chunk)
                
                # Prepare for vector store
                embeddings.append(embedding)
                chunk_metadata.append({
                    'document_id': document_id,
                    'filename': filename,
                    'chunk_index': i,
                    'text': chunk_text,
                    'page_number': None
                })
            
            # Add to vector store
            vector_store.add_embeddings(embeddings, chunk_metadata)
            
            # Commit database changes
            db.session.commit()
            
            # Save vector store
            vector_store.save_to_file('vector_store')
            
            return jsonify({
                'message': 'Document uploaded and processed successfully',
                'document_id': document_id,
                'filename': filename,
                'chunks_created': len(chunks)
            }), 201
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error processing document: {str(e)}'}), 500

@research_bp.route('/chat', methods=['POST'])
def chat_with_documents():
    """Chat with uploaded documents"""
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query']
        document_ids = data.get('document_ids', None)
        
        # Use RAG service to get answer
        result = rag_service.chat_with_documents(query, document_ids)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': f'Error processing chat request: {str(e)}'}), 500

@research_bp.route('/documents', methods=['GET'])
def get_documents():
    """Get list of all uploaded documents"""
    try:
        documents = Document.query.all()
        return jsonify({
            'documents': [doc.to_dict() for doc in documents]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error retrieving documents: {str(e)}'}), 500

@research_bp.route('/delete-document/<document_id>', methods=['DELETE'])
def delete_document(document_id):
    """Delete a document and its chunks"""
    try:
        # Find document
        document = Document.query.filter_by(document_id=document_id).first()
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        # Delete chunks
        DocumentChunk.query.filter_by(document_id=document_id).delete()
        
        # Delete document
        db.session.delete(document)
        db.session.commit()
        
        # Note: In a production system, you would also need to rebuild the vector store
        # to remove the deleted document's embeddings
        
        return jsonify({'message': 'Document deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error deleting document: {str(e)}'}), 500

@research_bp.route('/summarize-document/<document_id>', methods=['POST'])
def summarize_document(document_id):
    """Generate a summary of a specific document"""
    try:
        document = Document.query.filter_by(document_id=document_id).first()
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        data = request.get_json() or {}
        max_bullets = data.get('max_bullets', 5)
        
        summary = rag_service.summarize_document(document.content, max_bullets)
        
        return jsonify({
            'document_id': document_id,
            'filename': document.filename,
            'summary': summary
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error generating summary: {str(e)}'}), 500

def initialize_vector_store():
    """Initialize vector store on app startup"""
    global vector_store
    try:
        vector_store.load_from_file('vector_store')
        print("Vector store loaded from file")
    except Exception as e:
        print(f"Could not load vector store from file: {e}")
        print("Starting with empty vector store")

