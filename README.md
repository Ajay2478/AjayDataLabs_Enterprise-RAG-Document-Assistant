# 🤖 AjayDataLabs – AI-Based PDF Intelligence System  
**(College Project – Individual Contribution)**

---

## 📌 Project Status

✅ Completed
📅 Submission: February 2026  
👨‍💻 Developer: Ajay Kurchami (B.Sc. Data Science)

---

## 📖 1. Introduction

This project is an AI-powered document intelligence system that enables users to upload PDF documents and interact with them using natural language.

The system allows users to:

- Ask questions from documents  
- Receive citation-backed answers  
- Generate summaries  
- Access chat history  

The goal is to improve document understanding and reduce manual reading time.

---

## 🎯 2. Problem Statement

Reading and analyzing large documents such as reports, manuals, and legal files is time-consuming and inefficient.

Traditional search tools do not provide:

- Context-aware answers  
- Page-level references  
- Intelligent summarization  

This project addresses these limitations using AI-based retrieval and reasoning.

---

## ⚙️ 3. Proposed Solution

The system uses a **Retrieval-Augmented Generation (RAG)** approach.

### Workflow

1. User uploads a PDF  
2. Text is extracted from the document  
3. Content is split into chunks  
4. Embeddings are generated  
5. Vectors are stored in FAISS  
6. Relevant content is retrieved  
7. AI generates context-based answers  

This ensures that responses are based only on the uploaded document.

---

## 🏗️ 4. System Architecture

The system follows a client-server model:

- Frontend (React): User interface  
- Backend (FastAPI): Processing and AI logic  
- Vector Database (FAISS): Document memory  
- LLM (Groq Llama-3): Reasoning engine  
- SQLite: Chat and document history  

*(Insert Architecture Diagram Here)*

---

## 🛠️ 5. Technology Stack

| Layer      | Technology                     |
|------------|--------------------------------|
| Frontend   | React.js, CSS, Axios            |
| Backend    | Python, FastAPI, Uvicorn        |
| AI Models  | Groq Llama-3, Google GenAI      |
| Vector DB  | FAISS                           |
| Database   | SQLite                          |
| Deployment | Vercel, Railway                 |

---

## 💡 6. Key Features

- 📄 PDF Upload and Viewer  
- 💬 AI-Powered Question Answering  
- 📑 Document Summarization  
- 🔍 Page-Level Citations  
- 🕓 Chat History Storage  
- 🔊 Text-to-Speech Support  

---

## 🧑‍💻 7. Individual Contribution

This project was developed independently.

My responsibilities included:

- Backend API development  
- RAG pipeline implementation  
- Vector database integration  
- Frontend design and logic  
- Deployment configuration  
- Testing and debugging  
- Documentation preparation  

---

## 📊 8. Evaluation and Results

- Accurate document-based responses  
- Reduced hallucinations  
- Fast query processing  
- Successful deployment  
- Stable performance during testing  

User testing showed improved document comprehension efficiency.

---

## 📚 9. Learning Outcomes

Through this project, I learned:

- RAG system architecture  
- AI model integration  
- REST API development  
- React frontend development  
- Cloud deployment  
- Secure API management  
- Version control using Git  

---

## 🚀 10. Future Enhancements

Planned improvements include:

- Multi-document querying  
- OCR support for scanned PDFs  
- User authentication  
- Cloud database integration  
- Advanced analytics dashboard  

---

## 🔧 11. Installation Guide

### Backend Setup & Frontend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload


cd frontend
npm install
npm run dev
