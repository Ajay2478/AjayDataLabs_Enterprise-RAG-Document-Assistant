# System Architecture

## Overview

This project follows a client-server architecture using a Retrieval-Augmented Generation (RAG) pipeline.

It is designed to enable accurate and efficient document-based question answering.

---

## Components

### 1. Frontend (React.js)
- Provides user interface
- Handles PDF upload
- Displays chat responses
- Communicates with backend via REST API

### 2. Backend (FastAPI)
- Manages API endpoints
- Handles document processing
- Controls RAG pipeline
- Connects to AI models

### 3. Vector Database (FAISS)
- Stores document embeddings
- Enables semantic search
- Retrieves relevant chunks

### 4. Large Language Model (Groq Llama-3)
- Generates answers
- Performs reasoning
- Uses retrieved context

### 5. Database (SQLite)
- Stores chat history
- Stores document metadata

---

## Architecture Flow

User → React Frontend → FastAPI Backend  
FastAPI → FAISS → LLM → Response  
FastAPI → SQLite → History

---

## Benefits

- Modular design
- Scalable architecture
- Low latency
- High reliability
- Easy maintenance
