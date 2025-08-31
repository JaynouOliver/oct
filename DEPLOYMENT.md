# Deployment Guide for Render

## Render Configuration

### Manual Setup
1. **Root Directory**: Leave empty (use repository root)
2. **Build Command**: `pip install -r requirements.txt`
3. **Start Command**: `uvicorn api.rag_api:app --host 0.0.0.0 --port $PORT`

### Environment Variables
Set these in Render dashboard:
- `PYTHON_VERSION`: `3.11.0`
- Any API keys your application needs

### Automatic Deployment
If you have `render.yaml` in your repository, Render will automatically configure the service.

## File Structure
```
/
├── api/
│   └── rag_api.py          # Main FastAPI application
├── rag/
│   └── simple_rag.py       # RAG implementation
├── od-parse/               # Local package
├── requirements.txt        # Python dependencies
├── render.yaml            # Render configuration
├── Procfile              # Alternative deployment config
├── runtime.txt           # Python version specification
└── wsgi.py              # WSGI entry point
```

## Testing Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Run the API
uvicorn api.rag_api:app --host 0.0.0.0 --port 8000

# Or use the WSGI entry point
python wsgi.py
```

## Notes
- The virtual environment in `od-parse/` is for development only
- Render will create its own environment during deployment
- All dependencies are specified in `requirements.txt`
- The local `od-parse` package is installed via `-e ./od-parse`
