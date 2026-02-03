# RAG Pipeline Explanation

## Introduction

This project uses a Retrieval-Augmented Generation (RAG) architecture to ensure that AI responses are based only on uploaded documents.

---

## Pipeline Stages

### 1. Document Upload
- User uploads PDF
- File stored in server

### 2. Text Extraction
- PDFPlumber extracts text
- Metadata preserved

### 3. Chunking
- Text split into smaller segments
- Overlapping chunks used

### 4. Embedding Generation
- Google GenAI embeddings created
- Text converted into vectors

### 5. Vector Storage
- Embeddings stored in FAISS
- Enables fast similarity search

### 6. Retrieval
- Relevant chunks fetched
- Based on user query

### 7. Answer Generation
- LLM receives context
- Generates factual response

---

## Advantages

- Reduces hallucination
- Improves accuracy
- Enables citation support
- Works with large documents

---

## Optimization

- Chunk size tuning
- Retrieval depth tuning
- Prompt engineering
- Embedding quality improvement
