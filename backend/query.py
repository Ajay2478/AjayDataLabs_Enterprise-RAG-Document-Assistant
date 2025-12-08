import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# 1. Load API Key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Error: GOOGLE_API_KEY not found. Check your .env file.")
    exit()

# 2. Setup Memory (Vector DB)
DB_FAISS_PATH = "vectorstore/db_faiss"
# Using the same embeddings as your ingestion (likely HuggingFace if running locally)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

print("--- Loading Vector DB ---")
try:
    db = FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
except Exception as e:
    print(f"Error loading DB: {e}")
    exit()

# 3. Setup Brain
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)

# 4. Define Helper
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# 5. Create Chain (Updated with Polite Prompt)
template = """
You are a helpful AI assistant for a PDF Data Reader.
Your task is to answer the user's question based ONLY on the provided context below.

Rules:
1. If the answer is not present in the context, DO NOT make up an answer.
2. Instead, reply exactly with this polite message:
"I checked the document for you, but it doesn't seem to mention that. Is there a different section you'd like me to summarize?"

Context:
{context}

Question: {question}
"""

prompt = ChatPromptTemplate.from_template(template)

retriever = db.as_retriever(search_kwargs={'k': 3})

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 6. Run Loop
if __name__ == "__main__":
    print("\n--- AI PDF Assistant Ready! (Type 'exit' to quit) ---")
    while True:
        user_input = input("\nAsk a question: ")
        if user_input.lower() == "exit":
            break
        
        try:
            response = rag_chain.invoke(user_input)
            print("\n>> AI Answer:")
            print(response)
        except Exception as e:
            print(f"Error: {e}")