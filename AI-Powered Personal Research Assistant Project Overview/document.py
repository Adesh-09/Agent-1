from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.String(36), unique=True, nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    file_type = db.Column(db.String(50), nullable=False)
    
    def to_dict(self):
        return {
            'document_id': self.document_id,
            'filename': self.filename,
            'upload_date': self.upload_date.isoformat(),
            'file_type': self.file_type
        }

class DocumentChunk(db.Model):
    __tablename__ = 'document_chunks'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.String(36), db.ForeignKey('documents.document_id'), nullable=False)
    chunk_index = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    page_number = db.Column(db.Integer, nullable=True)
    embedding = db.Column(db.Text, nullable=True)  # Store as JSON string
    
    def to_dict(self):
        return {
            'document_id': self.document_id,
            'chunk_index': self.chunk_index,
            'text': self.text,
            'page_number': self.page_number
        }
    
    def set_embedding(self, embedding_vector):
        """Store embedding as JSON string"""
        self.embedding = json.dumps(embedding_vector)
    
    def get_embedding(self):
        """Retrieve embedding as list"""
        if self.embedding:
            return json.loads(self.embedding)
        return None

