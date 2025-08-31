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
        # Get query embedding
        query_embedding = self.openai_client.embeddings.create(
            model='text-embedding-3-small',
            input=[question]
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
            'answer': response.choices[0].message.content,
            'context': results['documents'][0]
        }

def main():
    rag = SimpleRAG()
    
    # Load and store data
    rag.load_and_store('intelligent_analysis_output/document_analysis.json')
    
    # Demo queries
    questions = [
        "What is the main topic of this research paper?",
        "What are the key findings about tax filing?",
        "What models were compared in the experiments?"
    ]
    
    print("\n🔍 Demo Queries:")
    for q in questions:
        result = rag.query(q)
        print(f"\nQ: {q}")
        print(f"A: {result['answer']}")

if __name__ == "__main__":
    main()
