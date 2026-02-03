from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import os
import shutil
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

# ---------------- AI IMPORTS ----------------
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


# ---------------- SETUP ----------------
load_dotenv()

app = FastAPI(title="AI PDF Assistant API")


# ---------------- PATHS (CLOUD SAFE) ----------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_DIR = os.path.join(BASE_DIR, "runtime_uploads")
FAISS_DIR = os.path.join(BASE_DIR, "runtime_faiss")

SQLITE_DB = os.path.join(BASE_DIR, "history.db")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(FAISS_DIR, exist_ok=True)

DB_FAISS_PATH = FAISS_DIR
UPLOAD_FOLDER = UPLOAD_DIR


# ---------------- HELPERS ----------------

def check_faiss_exists():
    return (
        os.path.exists(os.path.join(DB_FAISS_PATH, "index.faiss")) and
        os.path.exists(os.path.join(DB_FAISS_PATH, "index.pkl"))
    )


# ---------------- MIDDLEWARE ----------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=UPLOAD_FOLDER), name="static")


# ---------------- KEYS ----------------

google_api_key = os.getenv("GOOGLE_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

if not google_api_key:
    print("WARNING: GOOGLE_API_KEY missing")

if not groq_api_key:
    print("WARNING: GROQ_API_KEY missing")


# ---------------- MODELS ----------------

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    google_api_key=google_api_key
)

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3,
    groq_api_key=groq_api_key
)


# ---------------- DATABASE ----------------

def init_db():

    conn = sqlite3.connect(SQLITE_DB)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            upload_date TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT,
            timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()


# ---------------- REQUEST MODEL ----------------

class QueryRequest(BaseModel):
    question: str


# ---------------- ROUTES ----------------

@app.get("/")
def home():
    return {"message": "AI PDF API Running on Groq Llama-3!"}


@app.get("/documents")
def get_documents():

    conn = sqlite3.connect(SQLITE_DB)
    c = conn.cursor()

    c.execute("SELECT filename, upload_date FROM documents ORDER BY id DESC")

    docs = [
        {"filename": row[0], "date": row[1]}
        for row in c.fetchall()
    ]

    conn.close()

    return {"documents": docs}


@app.get("/history")
def get_history():

    conn = sqlite3.connect(SQLITE_DB)
    c = conn.cursor()

    c.execute("SELECT role, content FROM chats ORDER BY id ASC")

    history = [
        {"type": row[0], "text": row[1]}
        for row in c.fetchall()
    ]

    conn.close()

    return {"history": history}


@app.delete("/clear")
def clear_all():

    conn = sqlite3.connect(SQLITE_DB)
    c = conn.cursor()

    c.execute("DELETE FROM chats")
    c.execute("DELETE FROM documents")

    conn.commit()
    conn.close()

    return {"message": "History cleared"}


# ---------------- UPLOAD ----------------

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    try:

        print("Starting upload...")

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)

        # Save PDF
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print("Saved file:", file_path)

        # Load PDF
        loader = PDFPlumberLoader(file_path)
        docs = loader.load()

        if not docs:
            raise Exception("No text extracted")

        print("Pages:", len(docs))

        # Split
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

        chunks = splitter.split_documents(docs)

        print("Chunks:", len(chunks))

        # Create FAISS
        db = FAISS.from_documents(chunks, embeddings)

        db.save_local(DB_FAISS_PATH)

        print("FAISS saved:", DB_FAISS_PATH)

        # Save metadata
        conn = sqlite3.connect(SQLITE_DB)
        c = conn.cursor()

        c.execute(
            "INSERT INTO documents (filename, upload_date) VALUES (?, ?)",
            (file.filename, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )

        conn.commit()
        conn.close()

        return {
            "status": "success",
            "filename": file.filename
        }

    except Exception as e:

        print("UPLOAD FAILED:", e)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ---------------- SUMMARIZE ----------------

@app.post("/summarize")
async def summarize_document():

    try:

        if not check_faiss_exists():
            raise HTTPException(
                status_code=400,
                detail="Please upload a document first."
            )

        db = FAISS.load_local(
            DB_FAISS_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )

        retriever = db.as_retriever(search_kwargs={"k": 10})

        prompt = ChatPromptTemplate.from_template("""
You are an expert summarizer.

Context:
{context}
""")

        def format_docs(docs):
            return "\n\n".join(d.page_content for d in docs)

        chain = (
            {"context": retriever | format_docs}
            | prompt
            | llm
            | StrOutputParser()
        )

        summary = chain.invoke("Give full summary")

        conn = sqlite3.connect(SQLITE_DB)
        c = conn.cursor()

        c.execute(
            "INSERT INTO chats (role, content, timestamp) VALUES (?, ?, ?)",
            ("ai", summary, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )

        conn.commit()
        conn.close()

        return {"summary": summary}

    except HTTPException:
        raise

    except Exception as e:
        return {"summary": f"SYSTEM ERROR: {str(e)}"}


# ---------------- QUERY ----------------

@app.post("/query")
async def ask_question(request: QueryRequest):

    try:

        if not check_faiss_exists():
            raise HTTPException(
                status_code=400,
                detail="Please upload a document first."
            )

        conn = sqlite3.connect(SQLITE_DB)
        c = conn.cursor()

        c.execute(
            "INSERT INTO chats (role, content, timestamp) VALUES (?, ?, ?)",
            ("user", request.question, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )

        conn.commit()

        db = FAISS.load_local(
            DB_FAISS_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )

        retriever = db.as_retriever(search_kwargs={"k": 5})

        prompt = ChatPromptTemplate.from_template("""
You are a helpful AI assistant.

Use only the context.

Context:
{context}

Question:
{question}
""")

        def format_docs(docs):
            return "\n\n".join(
                f"[Page {d.metadata.get('page',0)+1}]: {d.page_content}"
                for d in docs
            )

        rag_chain = (
            {
                "context": retriever | format_docs,
                "question": RunnablePassthrough()
            }
            | prompt
            | llm
            | StrOutputParser()
        )

        answer = rag_chain.invoke(request.question)

        c.execute(
            "INSERT INTO chats (role, content, timestamp) VALUES (?, ?, ?)",
            ("ai", answer, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )

        conn.commit()
        conn.close()

        return {"answer": answer}

    except HTTPException:
        raise

    except Exception as e:
        return {"answer": f"SYSTEM ERROR: {str(e)}"}
