import os
from dotenv import load_dotenv

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


# =============================
# Load Environment
# =============================
load_dotenv()

GOOGLE_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_KEY = os.getenv("GROQ_API_KEY")

if not GOOGLE_KEY or not GROQ_KEY:
    print("❌ API keys missing")
    exit()


# =============================
# Load Vector DB
# =============================
DB_PATH = "vectorstore/db_faiss"

print("📂 Loading Vector DB...")

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    google_api_key=GOOGLE_KEY
)

db = FAISS.load_local(
    DB_PATH,
    embeddings,
    allow_dangerous_deserialization=True
)

retriever = db.as_retriever(search_kwargs={"k": 10})


# =============================
# Load LLM
# =============================
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.2,
    groq_api_key=GROQ_KEY
)


# =============================
# Prompt
# =============================
prompt = ChatPromptTemplate.from_template("""
You are a document analysis assistant.

Rules:
- Answer strictly from the context
- Extract exact factual information
- Do not say "not stated" if information is present
- Be concise and direct

Context:
{context}

Question:
{question}
""")



def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)


rag_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough()
    }
    | prompt
    | llm
    | StrOutputParser()
)


# =============================
# RBI TEST QUESTIONS
# =============================
test_cases = [

    {
        "question": "Which organization published this report?",
        "expected": "Reserve Bank of India"
    },

    {
        "question": "What is the main objective of this report?",
        "expected": "artificial intelligence"
    },

    {
        "question": "In which year was the report published?",
        "expected": "2025"
    },

    {
        "question": "What does FREE-AI stand for?",
        "expected": "Fairness"
    },

    {
        "question": "How many guiding principles are mentioned?",
        "expected": "7"
    }

]


# =============================
# Evaluation
# =============================
def run_test():

    print("\n🧪 Running Accuracy Test on RBI AI.pdf\n")

    correct = 0

    for i, case in enumerate(test_cases, 1):

        print(f"Q{i}: {case['question']}")

        answer = rag_chain.invoke(case["question"])

        print("AI:", answer)
        print("Expected:", case["expected"])

        if case["expected"].lower() in answer.lower():
            print("✅ Correct\n")
            correct += 1
        else:
            print("❌ Wrong\n")

    accuracy = (correct / len(test_cases)) * 100

    print("=" * 50)
    print(f"📊 Accuracy: {accuracy:.2f}%")
    print("=" * 50)


# =============================
# Run
# =============================
if __name__ == "__main__":
    run_test()
