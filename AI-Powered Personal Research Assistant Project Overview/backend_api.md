# Backend API Endpoints

## 1. Document Upload
- **Endpoint:** `/upload-document`
- **Method:** `POST`
- **Description:** Allows users to upload documents (PDFs, text files, etc.) to be processed and added to the knowledge base.
- **Request Body:**
    - `file`: (File) The document file to upload.
- **Response:**
    - `message`: (String) Confirmation message.
    - `document_id`: (String) Unique identifier for the uploaded document.

## 2. Chat with Knowledge Base
- **Endpoint:** `/chat`
- **Method:** `POST`
- **Description:** Enables users to ask questions in natural language and receive answers from the knowledge base with citations.
- **Request Body:**
    - `query`: (String) The user's natural language question.
    - `document_ids`: (List[String], Optional) A list of document IDs to chat with. If not provided, chats with all available documents.
- **Response:**
    - `answer`: (String) The LLM-generated answer.
    - `citations`: (List[Object]) A list of citations, each containing:
        - `document_id`: (String) The ID of the document the citation came from.
        - `page_number`: (Integer, Optional) The page number within the document.
        - `text`: (String) The exact passage/section cited.

## 3. Document List
- **Endpoint:** `/documents`
- **Method:** `GET`
- **Description:** Retrieves a list of all uploaded documents.
- **Response:**
    - `documents`: (List[Object]) A list of document objects, each containing:
        - `document_id`: (String) Unique identifier for the document.
        - `filename`: (String) Original filename of the document.
        - `upload_date`: (String) Timestamp of when the document was uploaded.

## 4. Document Deletion
- **Endpoint:** `/delete-document/{document_id}`
- **Method:** `DELETE`
- **Description:** Deletes a specific document from the knowledge base.
- **Parameters:**
    - `document_id`: (String) The ID of the document to delete.
- **Response:**
    - `message`: (String) Confirmation message.

