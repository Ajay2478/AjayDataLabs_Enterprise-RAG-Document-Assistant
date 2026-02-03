import os
import tempfile
from dotenv import load_dotenv

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


# Load keys
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GOOGLE_API_KEY or not GROQ_API_KEY:
    print("Missing API keys in .env")
    exit()


# FAISS path (same as main.py)
TEMP_DIR = tempfile.gettempdir()
DB_FAISS_PATH = os.path.join(TEMP_DIR, "db_faiss")


# Embeddings
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    google_api_key=GOOGLE_API_KEY
)


# Load DB
print("Loading vector DB...")

if not os.path.exists(os.path.join(DB_FAISS_PATH, "index.faiss")):
    print("No vector DB found. Upload PDF first.")
    exit()

db = FAISS.load_local(
    DB_FAISS_PATH,
    embeddings,
    allow_dangerous_deserialization=True
)


# LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3,
    groq_api_key=GROQ_API_KEY
)


# Prompt
prompt = ChatPromptTemplate.from_template("""
Answer strictly from context.

Context:
{context}

Question:
{question}
""")


# Retriever
retriever = db.as_retriever(search_kwargs={"k": 5})


def format_docs(docs):
    return "\n\n".join(
        f"[Page {d.metadata.get('page',0)+1}]: {d.page_content}"
        for d in docs
    )


# Chain
rag_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough()
    }
    | prompt
    | llm
    | StrOutputParser()
)


# CLI Loop
print("\n--- AI PDF Assistant Ready (CLI Mode) ---")

while True:

    q = input("\nAsk: ")

    if q.lower() == "exit":
        break

    try:
        answer = rag_chain.invoke(q)
        print("\n>> Answer:\n", answer)

    except Exception as e:
        print("Error:", e)
