"Langhcain RAG system for answering questions from a PDF document"
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate


def format_docs(docs):
    "Join the page content of the documents"
    return "\n\n".join(doc.page_content for doc in docs)


def pdf_rags(code_question: str,
             pdf_path="data/cadquery-readthedocs-io-en-latest.pdf",
             persist_directory="./Cadquery_db") -> str:
    "RAG system for answering questions from a PDF document"
    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2")

    # Initialize LLM
    llm = ChatGroq(model="llama3-8b-8192", api_key=os.environ["GROQ_API_KEY"])

    # Check if the vector store already exists
    if os.path.exists(persist_directory):
        # Load existing vector store
        vectorstore = Chroma(
            collection_name="CadQuery_Documentation",
            embedding_function=embeddings,
            persist_directory=persist_directory
        )
        print("Loaded existing vector store.")
    else:
        # If vector store doesn't exist, create it
        # Load and split the document
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=256, chunk_overlap=50, separators=[
                "\n\n", "\n", ". ", " ", ""])
        all_splits = text_splitter.split_documents(documents)

        # Create and persist the vector store
        vectorstore = Chroma.from_documents(
            collection_name="CadQuery_Documentation",
            documents=all_splits,
            embedding=embeddings,
            persist_directory=persist_directory
        )
        print("Created and persisted new vector store.")

    # Create retriever
    retriever = vectorstore.as_retriever()

    template = """Use the following pieces of context to answer the question
    at the end regarding using CadQuery methods, classes and api to create CAD models.
    If you don't know the answer, just say that you don't know, 
    don't try to make up an answer.
    Provide code snippet relevant to the question only.

    {context}

    Question: {question}

    Helpful Answer:"""
    custom_rag_prompt = PromptTemplate.from_template(template)

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | custom_rag_prompt
        | llm
        | StrOutputParser()
    )

    response = rag_chain.invoke(code_question)

    # Invoke the chain
    # response = rag_chain.invoke({"input": code_question})
    return response


# Example usage
if __name__ == "__main__":
    while True:
        question = input("Enter your question regarding Cadquery: ")
        print(pdf_rags(question))
