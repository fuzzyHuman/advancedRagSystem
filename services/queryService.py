from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain.document_loaders import TextLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Pinecone as langPinecone
from pinecone.grpc import PineconeGRPC as Pinecone
from dotenv import load_dotenv
from pinecone import ServerlessSpec
from langchain_openai import AzureChatOpenAI
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
import streamlit as st
from langchain import PromptTemplate
from services.databaseRetrieval import get_summary_by_index_name,get_policy_questions,get_answer_by_index_and_id
#import pinecone
import os

def initialize_llm():
    return AzureChatOpenAI(
        openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        deployment_name="gpt-4",
        model="gpt-4",
        temperature=0.3,
        openai_api_version="2024-02-01",
    )

def process_user_query(question):
    if 'index_name' not in st.session_state:
        return "Please upload an insurance document before asking questions."
    
    index_name = st.session_state.index_name

    llm = initialize_llm()
    summary = get_summary_by_index_name(index_name)

    # Retrieve all policy questions along with their IDs
    questions = get_policy_questions(index_name)

    # Create a prompt to analyze the question and match it with existing questions
    match_prompt_template = """
    You are an expert in insurance policies. The user has asked the following question:
    "{user_question}"
    Here is a list of available questions from the database:
    {database_questions}
    Determine if any of the database questions match or closely answer the user's query.
    If a match is found, return the question and its ID without any modifications. If no match is found, return "No match found".
    """

    database_questions = "\n".join([f"ID: {q['id']}, Question: {q['question']}" for q in questions])
    
    match_prompt = PromptTemplate(
        template=match_prompt_template,
        input_variables=["user_question", "database_questions"]
    )

    # Directly use the prompt template and interact with the LLM
    match_response = llm(prompt=match_prompt.format(user_question=question, database_questions=database_questions))

    if "No match found" not in match_response:
        # Extract the matched question ID from the response
        matched_question_id = match_response.split("ID: ")[1].split(",")[0]
        answer = get_answer_by_index_and_id(index_name, matched_question_id)
        return answer
    else:
        # If no match is found, use RAG chain with the summary
        prompt = PromptTemplate(
            template="""
            You are an expert in solving Insurance queries. The following is the context given to you to answer
            the query given by the user. You are also given the overall detailed summary of the insurance document. Use both of them to 
            answer the query as best as you can.
            
            Context: {context}
            Summary: {summary}
            Question: {question}
            Answer:
            """,
            input_variables=["context", "summary", "question"]
        )

        # Initialize Pinecone client and docsearch
        client = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        embeddings = HuggingFaceEmbeddings()
        docsearch = langPinecone.from_existing_index(index_name, embeddings)

        rag_chain_with_summary = (
            {"context": docsearch.as_retriever(), "summary": RunnablePassthrough(summary), "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        
        response = rag_chain_with_summary.invoke({"context": "", "summary": summary, "question": question})
        return response