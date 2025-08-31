#!/usr/bin/env python3
"""
Simple RAG Pipeline - Minimal Implementation

Uses ChromaDB Cloud + OpenAI for embeddings and inference
"""

import json
import os
import chromadb
import openai
from pathlib import Path
from dotenv import load_dotenv

# Load config
load_dotenv()

class SimpleRAG:
    def __init__(self):
        # ChromaDB Cloud
        self.client = chromadb.CloudClient(
            api_key=os.getenv('CHROMA_API_KEY'),
            tenant=os.getenv('CHROMA_TENANT'),
            database=os.getenv('CHROMA_DATABASE', 'ai_agent')
        )
        self.collection = self.client.get_or_create_collection('documents')
        
        # OpenAI
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def restructure_query(self, question: str) -> str:
        """Restructure the user question into a better search query."""
        try:
            response = self.openai_client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {
                        "role": "system", 
                        "content": """You are a query reformulation expert. Your job is to restructure user questions into better search queries for a RAG system that contains research paper content.

Rules:
1. Fix grammar and spelling errors
2. Expand abbreviations and acronyms
3. Add relevant keywords that might appear in the document
4. Make the query more specific and searchable
5. If the question mentions figures, tables, or specific content, include those terms
6. Keep the original intent but make it more formal and complete

Examples:
- "what is there is figure 1" → "What does Figure 1 show? What is the content and meaning of Figure 1?"
- "tax filing costs" → "What are the costs and expenses associated with tax filing?"
- "SARA dataset" → "What is the SARA dataset? Explain the StAtutory Reasoning Assessment dataset"
- "model comparison" → "What models were compared in the experiments? Which models were evaluated?"

Return only the restructured query, nothing else."""
                    },
                    {
                        "role": "user",
                        "content": f"Restructure this question: {question}"
                    }
                ],
                max_tokens=100,
                temperature=0.1
            )
            
            restructured = response.choices[0].message.content.strip()
            print(f"Original query: {question}")
            print(f"Restructured query: {restructured}")
            return restructured
            
        except Exception as e:
            print(f"Error restructuring query: {e}")
            return question  # Fallback to original question
    
    def load_and_store(self, json_file: str):
        """Load JSON and store in ChromaDB"""
        with open(json_file) as f:
            data = json.load(f)
        
        chunks = data.get('rag_chunks', [])
        if not chunks:
            print("No chunks found in JSON")
            return
        
        # Check if chunks already exist
        existing_count = self.collection.count()
        if existing_count > 0:
            print(f"{existing_count} chunks already exist in ChromaDB Cloud")
            return
        
        # Prepare data
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        documents = [chunk['content'] for chunk in chunks]
        metadatas = [{'type': chunk['type'], 'source': chunk['source']} for chunk in chunks]
        
        # Generate embeddings and store
        embeddings = self.openai_client.embeddings.create(
            model='text-embedding-3-small',
            input=documents
        ).data
        
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=[e.embedding for e in embeddings]
        )
        
        print(f"Stored {len(chunks)} chunks in ChromaDB Cloud")
    
    def query(self, question: str, top_k: int = 3):
        """Query with RAG"""
        # Restructure the query first
        restructured_question = self.restructure_query(question)
        
        # Get query embedding
        query_embedding = self.openai_client.embeddings.create(
            model='text-embedding-3-small',
            input=[restructured_question]
        ).data[0].embedding
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        # Prepare context
        context = "\n\n".join(results['documents'][0])
        
        # Generate answer
        response = self.openai_client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {"role": "system", "content": "Answer based on the provided context."},
                {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"}
            ],
            max_tokens=500,
            temperature=0.1
        )
        
        return {
            'question': question,
            'restructured_question': restructured_question,
            'answer': response.choices[0].message.content,
            'context': results['documents'][0]
        }
    
    def get_collection_info(self):
        """Get information about the current collection"""
        try:
            count = self.collection.count()
            return {
                'collection_name': self.collection.name,
                'chunk_count': count
            }
        except Exception as e:
            return {'error': str(e)}
    
    def setup_document(self, json_file: str):
        """
        Simple function to check if embeddings exist and upload if needed
        
        Args:
            json_file: Path to the JSON file with RAG chunks
        """
        print(f"Setting up document: {json_file}")
        print(f"Collection: {self.collection.name}")
        
        # Check current status
        info = self.get_collection_info()
        if 'error' not in info:
            print(f"Current chunks in collection: {info['chunk_count']}")
        
        # Load and store (this function already checks if chunks exist)
        self.load_and_store(json_file)
        
        # Final status
        final_info = self.get_collection_info()
        if 'error' not in final_info:
            print(f"Ready! {final_info['chunk_count']} chunks available for querying")
        else:
            print(f"Error: {final_info['error']}")

# Usage example:
# from rag.simple_rag import SimpleRAG
# rag = SimpleRAG()
# rag.setup_document('path/to/your/document.json')
