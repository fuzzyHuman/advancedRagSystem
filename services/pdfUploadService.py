import os
import streamlit as st
from langchain.chains.summarize import load_summarize_chain
from langchain_openai import AzureChatOpenAI
from PyPDF2 import PdfReader # type: ignore
from langchain.text_splitter import CharacterTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Initialize the Azure OpenAI model
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

# Summarize PDF content
def summarize_pdf(file, llm):
    # Read PDF content
    pdf = PdfReader(file)
    text = ""
    for page in pdf.pages:
        text += page.extract_text()

    text_splitter = RecursiveCharacterTextSplitter(
    # Set a really small chunk size, just to show.
    chunk_size=5000,
    chunk_overlap=500,
    length_function=len,
    is_separator_regex=False,
    )
    
    texts = text_splitter.create_documents(text)
    # Load summarization chain
    chain = load_summarize_chain(llm,chain_type="map_reduce")
    
    # Get the summary
    summary = chain.run(texts)
    return summary

# PDF Upload Service
def upload_pdf_service():
    st.sidebar.subheader("Upload PDF Documents")
    
    # Initialize the session state for uploaded files history
    if 'uploaded_files_history' not in st.session_state:
        st.session_state.uploaded_files_history = []

    if 'deleted_files' not in st.session_state:
        st.session_state.deleted_files = []

    uploaded_files = st.sidebar.file_uploader("Choose PDF files", accept_multiple_files=True, type="pdf")
    
    if uploaded_files:
        llm = initialize_llm()
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            # Add the uploaded file to the session state history
            if file_name not in st.session_state.uploaded_files_history:
                st.session_state.uploaded_files_history.append(file_name)
            
            st.sidebar.write(f"Uploaded: {file_name}")

            # Summarize the uploaded PDF
            summary = summarize_pdf(uploaded_file, llm)
            st.write(f"Summary of {file_name}: {summary}")

    # Display the upload history
    st.sidebar.subheader("Upload History")
    if st.session_state.uploaded_files_history:
        for file in st.session_state.uploaded_files_history:
            st.sidebar.write(f"You uploaded: {file}")

    # Display the deleted files history
    st.sidebar.subheader("Deleted Files")
    if st.session_state.deleted_files:
        for file in st.session_state.deleted_files:
            st.sidebar.write(f"You deleted: {file}")

# Placeholder for processing PDF files
def process_pdf(uploaded_file):
    st.write(f"Processing file: {uploaded_file.name}")