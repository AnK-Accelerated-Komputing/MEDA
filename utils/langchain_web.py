"""RAG with web"""
import os

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import AzureChatOpenAI
# from langchain_groq import ChatGroq #uncomment to use groq

def format_docs(docs):
    "Join the page content of the documents"
    return "\n\n".join(doc.page_content for doc in docs)


def web_rag(query: str):
    """
    Create a RAG system from URLs containing documentation.

    Args:
        prompt (str): Prompt for which relevant context is to be retrieved.

    Returns:
        qa_chain: A RetrievalQA chain that can answer questions
    """
    urls = [
        "https://cadquery.readthedocs.io/en/latest/apireference.html",
        "https://cadquery.readthedocs.io/en/latest/selectors.html",
        "https://cadquery.readthedocs.io/en/latest/classreference.html"
    ]
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2")

    llm = AzureChatOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_BASE"],
        azure_deployment="gpt-4o",
        openai_api_version="2024-08-01-preview",
        api_key=os.environ["AZURE_API_KEY"],
        temperature=0.1,
        max_retries=2,
    )
    #llm = ChatGroq(model="llama3-8b-8192", api_key=os.environ["GROQ_API_KEY"])
    #change your model name here
    persist_directory = "./Cadquery_web_db"
    # Load documents from URLs
    if os.path.exists(persist_directory):
        # Load existing vector store
        vectorstore = Chroma(
            collection_name="CadQuery_Documentation",
            embedding_function=embeddings,
            persist_directory=persist_directory
        )
        print("Loaded existing vector store.")
    else:
        loader = UnstructuredURLLoader(urls=urls)
        documents = loader.load()

        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        splits = text_splitter.split_documents(documents)

        # Create vector store
        vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=embeddings,
            persist_directory=persist_directory,

        )
        print("Created and persisted new vector store.")

    retriever = vectorstore.as_retriever(
        search_kwargs={'k': 3})
    template = """Use the following pieces of context to answer the question
    at the end regarding using CadQuery methods, classes and api to create CAD models.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
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
    response = rag_chain.invoke(query)

    return response


# if __name__ == "__main__":
#     PROMPT = "How to create a torus in cadquery?"
#     print(web_rag(PROMPT))
