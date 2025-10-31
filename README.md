# AI Chatbot with RAG (Retrieval-Augmented Generation)

A modern web application featuring an AI-powered chatbot with RAG capabilities. Upload documents to create a knowledge base, and the chatbot will use them to provide contextual, accurate responses.

## Features

- **AI-Powered Chatbot**: Leverages OpenAI's GPT models for intelligent conversations
- **RAG System**: Uses ChromaDB vector database for document retrieval
- **Document Upload**: Support for PDF and TXT files
- **Semantic Search**: Finds relevant context using sentence embeddings
- **Modern UI**: Clean, responsive interface built with vanilla JavaScript
- **Toggle RAG**: Switch between RAG-enhanced and standard chatbot modes
- **Real-time Updates**: Live document count and system status

## Architecture

### Backend
- **FastAPI**: Modern Python web framework
- **ChromaDB**: Vector database for document storage and retrieval
- **Sentence Transformers**: For creating document embeddings
- **OpenAI API**: Powers the chatbot responses

### Frontend
- **HTML/CSS/JavaScript**: No framework dependencies
- **Responsive Design**: Works on desktop and mobile
- **Real-time Communication**: Async API calls

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- pip (Python package manager)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd Contracting-Government-Expert
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```

4. **Edit `.env` file and add your OpenAI API key**:
   ```
   OPENAI_API_KEY=sk-your-api-key-here
   ```

## Usage

### Starting the Server

Run the application using Python:

```bash
python -m backend.main
```

Or use the run script:

```bash
python run.py
```

The server will start at `http://localhost:8000`

### Using the Application

1. **Open your browser** and navigate to `http://localhost:8000`

2. **Upload Documents**:
   - Click "Choose File" in the sidebar
   - Select a .txt or .pdf file
   - Click "Upload"
   - The document will be processed and added to the knowledge base

3. **Chat with the AI**:
   - Type your message in the text area at the bottom
   - Press Enter or click "Send"
   - The AI will respond using context from your uploaded documents (if RAG is enabled)

4. **Toggle RAG**:
   - Use the toggle switch to enable/disable RAG
   - When disabled, the chatbot responds without document context

5. **Clear Documents**:
   - Click "Clear All Documents" to remove all uploaded documents
   - This will reset the knowledge base

## API Endpoints

### Health Check
```
GET /api/health
```
Returns system status and document count.

### Chat
```
POST /api/chat
Body: {
  "message": "your question",
  "use_rag": true
}
```
Send a message and get an AI response.

### Upload Document
```
POST /api/upload
Body: FormData with file
```
Upload a document to the knowledge base.

### Get Document Count
```
GET /api/documents/count
```
Get the number of document chunks in the system.

### Clear Documents
```
DELETE /api/documents
```
Remove all documents from the knowledge base.

## Configuration

Edit the `.env` file to customize:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required |
| `HOST` | Server host | 0.0.0.0 |
| `PORT` | Server port | 8000 |
| `COLLECTION_NAME` | ChromaDB collection name | documents |
| `EMBEDDING_MODEL` | Sentence transformer model | sentence-transformers/all-MiniLM-L6-v2 |
| `CHUNK_SIZE` | Document chunk size | 1000 |
| `CHUNK_OVERLAP` | Chunk overlap | 200 |

## Project Structure

```
Contracting-Government-Expert/
├── backend/
│   ├── models/
│   │   └── schemas.py          # Pydantic models
│   ├── routes/
│   │   └── api.py              # API endpoints
│   ├── services/
│   │   ├── chat_service.py     # AI chat logic
│   │   └── rag_service.py      # RAG implementation
│   └── main.py                 # FastAPI application
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css      # Styling
│   │   └── js/
│   │       └── app.js          # Frontend logic
│   └── index.html              # Main page
├── documents/                   # Place for sample documents
├── .env                        # Environment variables
├── .env.example                # Example environment file
├── requirements.txt            # Python dependencies
├── run.py                      # Run script
└── README.md                   # This file
```

## How RAG Works

1. **Document Upload**: When you upload a document, it's split into chunks
2. **Embedding**: Each chunk is converted to a vector embedding
3. **Storage**: Embeddings are stored in ChromaDB
4. **Query**: When you ask a question, it's also converted to an embedding
5. **Retrieval**: Similar document chunks are retrieved using vector similarity
6. **Generation**: Retrieved chunks are sent to the AI as context
7. **Response**: The AI generates a response using the context

## Troubleshooting

### OpenAI API Error
- Make sure your API key is correct in `.env`
- Check you have credits in your OpenAI account
- Verify the API key has proper permissions

### Port Already in Use
- Change the PORT in `.env` to a different value
- Or kill the process using port 8000

### Module Not Found
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Make sure you're running from the project root directory

### Document Upload Fails
- Check file format (only .txt and .pdf supported)
- Ensure file size is reasonable
- Check server logs for errors

## Development

### Adding New Features

1. **Backend**: Add new routes in `backend/routes/api.py`
2. **Services**: Add business logic in `backend/services/`
3. **Frontend**: Update `frontend/static/js/app.js` for new UI features

### Testing

Test the API using curl:

```bash
# Health check
curl http://localhost:8000/api/health

# Send a chat message
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello", "use_rag":true}'
```

## Technologies Used

- **FastAPI**: Modern, fast web framework
- **ChromaDB**: Vector database
- **OpenAI**: GPT models
- **Sentence Transformers**: Document embeddings
- **PyPDF**: PDF processing
- **Uvicorn**: ASGI server

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on the GitHub repository.
