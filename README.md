# RMGX Assignment: AI-Powered Document Chat & Retrieval System

This project is a full-stack application that enables users to upload, manage, and chat with their documents using an advanced AI agent. The backend is built with FastAPI and integrates with MongoDB and Pinecone for storage and vector search. The AI agent (powered by Gemini) intelligently decides whether to answer from its own knowledge or to retrieve relevant information from your uploaded documents, providing step-by-step reasoning and transparent answers.

## Key Features

- **User Authentication:** Secure registration and login with JWT-based authentication.
- **Document Management:** Upload PDF documents (via file or URL), view all your documents, and delete them as needed.
- **AI Chat Agent:** Ask questions in natural language. The agent will:
  - Analyze your query and decide if it needs to search your documents or can answer directly.
  - Retrieve and synthesize relevant information from your documents using semantic search (Pinecone).
  - Provide clear, well-structured answers with reasoning, context, and references.
- **Chat History:** All conversations are stored and can be deleted or retrieved by the user.
- **Frontend Ready:** Designed for easy integration with a modern frontend (see API docs below).

## How It Works

1. **Upload Documents:** Users can upload PDFs either from their device or by providing a direct URL.
2. **Ask Questions:** Users interact with the AI agent via a chat interface. The agent uses advanced reasoning to decide:
   - Should it answer from its own knowledge?
   - Should it search the user's documents for evidence?
   - Should it combine both?
3. **Get Answers:** The agent responds in Markdown, with clear structure, references, and transparency about its sources.
4. **Manage Data:** Users can view, delete, and manage both their documents and chat history.

---

## Setup

### Prerequisites
- Python 3.8+ installed
- MongoDB instance (local or Atlas)
- Pinecone account for vector database
- Google API key for Gemini model

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd RMGX-assignment
   ```

2. **Set up Python virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   cd server
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the `server` directory with the following variables:
   ```
   # MongoDB settings
   MONGO_URI=mongodb://localhost:27017
   MONGO_DB=document_chat

   # JWT settings
   JWT_SECRET=your_jwt_secret_key
   JWT_ALGORITHM=HS256
   EXPIRATION_TIME=7  # Days

   # Pinecone settings
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_INDEX=your_pinecone_index

   # Google API settings
   GEMINI_API_KEY=your_gemini_api_key
   GEMINI_MODEL=gemini-pro
   GEMINI_EMBEDDING_MODEL=models/embedding-001
   ```

5. **Run the server**
   ```bash
   uvicorn app.main:app --reload
   ```
   The server will be available at http://localhost:8000

### Frontend Setup (Optional)

1. **Navigate to frontend directory**
   ```bash
   cd ../frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Create `.env.local` file**
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. **Run the development server**
   ```bash
   npm run dev
   ```
   The frontend will be available at http://localhost:3000

---

# API Documentation

This backend provides a document management and chat system with authentication, document upload, retrieval, deletion, and chat/querying capabilities.

## Base URL

Assume the backend is running at: `http://localhost:8000`

---

## Authentication

### Register
- **Endpoint:** `POST /auth/register`
- **Query Parameters:**
  - `email` (string)
  - `password` (string)
- **Example:**
  ```
  POST /auth/register?email=someone@email.com&password=yourpassword
  ```
- **Response:** `{ "access_token": <token> }`

### Login
- **Endpoint:** `POST /auth/login`
- **Query Parameters:**
  - `email` (string)
  - `password` (string)
- **Example:**
  ```
  POST /auth/login?email=someone@email.com&password=yourpassword
  ```
- **Response:** `{ "access_token": <token> }`

**Note:** Use the `access_token` as a Bearer token in the `Authorization` header for all protected endpoints.

---

## Documents

### Get All Documents
- **Endpoint:** `GET /documents/documents`
- **Headers:** `Authorization: Bearer <token>`
- **Response:**
  ```json
  [
    {
      "_id": "...",
      "user_id": "...",
      "doc_id": "...",
      "file_name": "...",
      "embedding_status": "complete"
    },
    ...
  ]
  ```

### Upload Document (File)
- **Endpoint:** `POST /documents/upload`
- **Headers:** `Authorization: Bearer <token>`
- **Body:** `multipart/form-data`
  - `file`: PDF file
- **Response:** `{ "status": "success", "document_id": "..." }`

### Upload Document (URL)
- **Endpoint:** `POST /documents/upload_url`
- **Headers:** `Authorization: Bearer <token>`
- **Query Parameter:**
  - `url`: Direct link to a PDF file
- **Example:**
  ```
  POST /documents/upload_url?url=https://example.com/file.pdf
  ```
- **Response:** `{ "status": "success", "document_id": "..." }`

### Delete Document
- **Endpoint:** `DELETE /documents/document/{doc_id}`
- **Headers:** `Authorization: Bearer <token>`
- **Response:** `{ "status": "success", "message": "Document deleted" }`

---

## Chat/Query

### Query
- **Endpoint:** `POST /chat/query`
- **Headers:** `Authorization: Bearer <token>`
- **Body:** `application/json`
  - `query`: (string) The user's question
  - `doc_ids`: (optional, array of strings) Restrict search to specific document IDs
- **Response:**
  ```json
  {
    "response": {
      "answer": "...",
      "tool_calls": [
        { "tool": "search_documents", "input": { ... } },
        ...
      ]
    }
  }
  ```