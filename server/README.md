# RMGX Assignment Backend API Documentation

This backend provides a document management and chat system with authentication, document upload, retrieval, deletion, and chat/querying capabilities. Use this documentation to build a frontend that interacts with the API.

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

---

## General Notes for Frontend

- All endpoints except `/auth/register` and `/auth/login` require authentication.
- Use the JWT token in the `Authorization` header for all requests after login/register.
- Document upload supports both file and URL (PDF only).
- The chat endpoint can optionally restrict the query to specific documents by passing their IDs.
- Deleting a document removes it from both the database and the vector store.
- Document list includes metadata such as file name and status.

---

## Example Usage Flow

1. **Register/Login** to get a token.
2. **Upload** documents (file or URL).
3. **List** all your documents.
4. **Chat** with the system, optionally specifying which documents to use.
5. **Delete** documents as needed.

---

## Suggested Frontend Features

- Login/Register page
- Document dashboard (list, upload, delete)
- Chat interface (with optional document selection)
- File upload and URL input for new documents
- Status/error handling for all API calls

---

For any questions about API usage, refer to this README or inspect the backend code for details on request/response formats.
