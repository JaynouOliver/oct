# RAG Document Q&A System - Setup Guide

A complete RAG (Retrieval-Augmented Generation) system using od-parse for document processing, ChromaDB Cloud for vector storage, and OpenAI for embeddings and generation.

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone the repository
git clone <your-repo>
cd oct

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file with your credentials:

```env
# ChromaDB Cloud Configuration
CHROMA_API_KEY=your_chroma_api_key
CHROMA_TENANT=your_chroma_tenant
CHROMA_DATABASE=your_database_name

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
```

### 3. Document Processing

```bash
# Parse your PDF using od-parse
python main.py
```

This will:
- Process the PDF using od-parse library
- Extract text, tables, and images
- Generate descriptions for images
- Create `intelligent_analysis_output/document_analysis.json`

### 4. Upload Embeddings

```python
# Start Python interpreter
python

# Import and setup RAG
from rag.simple_rag import SimpleRAG
rag = SimpleRAG()
rag.setup_document('intelligent_analysis_output/document_analysis.json')
```

This will:
- Check if embeddings already exist in ChromaDB
- Upload embeddings if they don't exist
- Show status: "Ready! X chunks available for querying"

### 5. Start the API Server

```bash
python api/rag_api.py
```

The API will be available at `http://localhost:8000`

### 6. Start the Frontend

```bash
cd frontend-next
npm install
npm run dev
```

Open `http://localhost:3000` in your browser

## 📁 Project Structure

```
oct/
├── main.py                           # PDF parsing with od-parse
├── rag/
│   └── simple_rag.py                 # RAG implementation
├── api/
│   └── rag_api.py                    # FastAPI server
├── frontend-next/                    # Next.js frontend
├── intelligent_analysis_output/
│   └── document_analysis.json        # Processed document
├── .env                              # Configuration
├── requirements.txt                  # Python dependencies
└── setup_guide.md                    # This file
```

## 🔧 Configuration Details

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `CHROMA_API_KEY` | ChromaDB Cloud API key | Yes |
| `CHROMA_TENANT` | ChromaDB Cloud tenant ID | Yes |
| `CHROMA_DATABASE` | ChromaDB database name | Yes |
| `OPENAI_API_KEY` | OpenAI API key | Yes |

### API Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check
- `POST /query` - Query the document

### Frontend Features

- Interactive Q&A interface
- Query restructuring display
- Context source viewing
- Demo questions
- Adjustable context chunks

## 🛠️ Usage Examples

### Query via API

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic?", "top_k": 3}'
```

### Query via Python

```python
from rag.simple_rag import SimpleRAG

rag = SimpleRAG()
result = rag.query("What is the main topic?")
print(result['answer'])
```

### Check Collection Status

```python
info = rag.get_collection_info()
print(f"Collection: {info['collection_name']}")
print(f"Chunks: {info['chunk_count']}")
```

## 🔍 Features

### Document Processing
- **Text Extraction**: Extracts all text content
- **Table Detection**: Identifies and extracts tables
- **Image Analysis**: Generates descriptions for figures
- **Smart Chunking**: Creates semantic chunks for RAG

### RAG Pipeline
- **Query Restructuring**: Improves search queries using LLM
- **Semantic Search**: Finds relevant chunks using embeddings
- **Context-Aware Answers**: Generates answers based on retrieved context
- **Multi-modal Support**: Handles text, tables, and image descriptions

### Frontend
- **Modern UI**: Clean, responsive interface
- **Real-time Queries**: Instant answers
- **Context Display**: Shows source chunks
- **Query History**: Tracks restructured queries

## 🚀 Deployment

### Local Development
```bash
# Terminal 1: API Server
python api/rag_api.py

# Terminal 2: Frontend
cd frontend-next && npm run dev
```

### Production
- Deploy API to cloud (Heroku, AWS, etc.)
- Deploy frontend to Vercel/Netlify
- Update CORS settings for production domains

## 📊 Monitoring

### API Health
```bash
curl "http://localhost:8000/health"
```

### Collection Status
```python
from rag.simple_rag import SimpleRAG
rag = SimpleRAG()
info = rag.get_collection_info()
print(info)
```

## 🔒 Security

- Store API keys in environment variables
- Use HTTPS in production
- Implement rate limiting if needed
- Add authentication for production use

## 📝 Troubleshooting

### Common Issues

1. **ChromaDB Connection Error**
   - Check API key and tenant ID
   - Verify database exists in ChromaDB Cloud

2. **OpenAI API Error**
   - Check API key
   - Verify account has credits

3. **Import Error**
   - Ensure virtual environment is activated
   - Install all dependencies: `pip install -r requirements.txt`

4. **CORS Error**
   - Check frontend URL in API CORS settings
   - Restart API server after changes

5. **PDF Processing Error**
   - Ensure PDF file exists
   - Check od-parse installation

## 🎯 Assignment Submission

This project demonstrates:

✅ **Complete RAG Pipeline**: PDF → Processing → Embeddings → Query
✅ **Modern Tech Stack**: od-parse + ChromaDB + OpenAI + Next.js
✅ **Query Restructuring**: Intelligent query improvement
✅ **Production Ready**: Error handling, monitoring, documentation
✅ **User Friendly**: Simple setup and usage
✅ **Modular Design**: Clean separation of concerns

## 📞 Support

For issues:
1. Check the troubleshooting section
2. Verify all dependencies are installed
3. Ensure environment variables are set correctly
4. Test with the example document first


