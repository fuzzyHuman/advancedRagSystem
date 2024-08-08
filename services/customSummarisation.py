import os
from dotenv import load_dotenv
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Pinecone as langPinecone
from pinecone.grpc import PineconeGRPC as Pinecone
from langchain_openai import AzureChatOpenAI
from langchain import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

def initialize_llm():
    model = AzureChatOpenAI(
        openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        deployment_name="gpt-4",
        model="gpt-4",
        temperature=0.3,
        openai_api_version="2024-02-01",
    )
    return model

def initialize_docsearch(index_name):
    load_dotenv()
    
    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings()

    # Initialize Pinecone client
    client = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
    
    # Link to the existing index
    docsearch = langPinecone.from_existing_index(index_name, embeddings)
    
    return docsearch

def ask_question(docsearch, question):
    # Initialize the LLM
    llm = initialize_llm()

    # Define the prompt template
    prompt = PromptTemplate(
        template="""
        You are a question-answering agent. A human will ask you a question.
        Use the following piece of context to answer the question.
        If you don't know the answer, just say you don't know.
        Keep the answer concise.

        Context: {context}
        Question: {question}
        Answer:
        """,
        input_variables=["context", "question"]
    )

    # Define the RAG chain
    rag_chain = (
        {"context": docsearch.as_retriever(), "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain.invoke(question)

def summarize_insurance_document(index_name):
    docsearch = initialize_docsearch(index_name)

    questions = [
        "What is the overall summary of the insurance document?",
        "What are the diseases covered in the insurance document?",
        "What are some of the benefits enlisted in the policy?"
    ]

    summaries = {}
    for question in questions:
        answer = ask_question(docsearch, question)
        summaries[question] = answer

    return summaries


