import os
import shutil
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PDFPlumberLoader  # <--- USE THIS

# 1. Load Environment Variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Error: GOOGLE_API_KEY not found. Check your .env file.")
    exit()

# 2. Setup Paths
PDF_PATH = "sample.pdf"
DB_FAISS_PATH = "vectorstore/db_faiss"

def create_vector_db():
    # --- Check if PDF exists ---
    if not os.path.exists(PDF_PATH):
        print(f"Error: '{PDF_PATH}' not found. Please add a PDF file named 'sample.pdf' to this folder.")
        return

    # --- SAFETY CHECK: Delete old DB ---
    if os.path.exists(DB_FAISS_PATH):
        print(f"Removing old vectorstore at {DB_FAISS_PATH}...")
        try:
            shutil.rmtree(DB_FAISS_PATH)
        except Exception as e:
            print(f"Warning: Could not delete old DB automatically. Delete '{DB_FAISS_PATH}' manually.")

    print(f"--- 1. Loading PDF from {PDF_PATH} ---")
    
    # Use PDFPlumber to keep Page Numbers (Metadata)
    loader = PDFPlumberLoader(PDF_PATH)
    docs = loader.load()
    
    if not docs:
        print("Error: No text extracted. File might be empty or image-based.")
        return

    # 3. Chunk the text
    print("--- 2. Splitting text into chunks ---")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    # Note: split_documents preserves metadata (page numbers)
    chunks = text_splitter.split_documents(docs) 
    print(f"Created {len(chunks)} chunks.")

    # 4. Create Embeddings
    print("--- 3. Creating Google Embeddings ---")
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=api_key)
    except Exception as e:
        print(f"Error initializing Embeddings: {e}")
        return

    # 5. Create and Save Vector Store
    print("--- 4. Saving to FAISS Vector DB ---")
    try:
        # Note: from_documents preserves metadata
        db = FAISS.from_documents(chunks, embeddings) 
        db.save_local(DB_FAISS_PATH)
        print(f"Success! Vector DB saved to: {DB_FAISS_PATH}")
    except Exception as e:
        print(f"Error saving DB: {e}")

if __name__ == "__main__":
    create_vector_db()