import os
import streamlit as st
from langchain.chains.summarize import load_summarize_chain
from langchain_openai import AzureChatOpenAI
from PyPDF2 import PdfReader # type: ignore
from langchain.text_splitter import CharacterTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain import PromptTemplate
from services.databaseRetrieval import get_index_name_by_policy_name,get_summary_by_index_name
from services.customSummarisation import summarize_insurance_document
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
def Name_and_details_extract(uploaded_file, llm):
    # Read the first page of the PDF content
    pdf = PdfReader(uploaded_file)
    first_page = pdf.pages[0]
    second_page = pdf.pages[1]
    
    text_first_page = first_page.extract_text()
    text_second_page = second_page.extract_text()
    # text_splitter = CharacterTextSplitter(
    # # Set a really small chunk size, just to show.
    # chunk_size=10000,
    # chunk_overlap=500,
    # )
    
    # texts = text_splitter.create_documents(combined_text)
    # # Load summarization chain
    # chain = load_summarize_chain(llm,chain_type="map_reduce")
    
    # Get the summary
    # summary = chain.run(texts)
      
    prompt_template = PromptTemplate(
    input_variables=["context", "query"],
    template="""
    Context: {context}
    
    Query: {query}
    
    Answer:
    """
    )
    query = """given is the summary page of an Insurance Policy , give me an output in the following form:
    
    Name of Policy: 
    Providing Company of the Policy: 
    
    if you dont find Name of the policy, only respond as "not found", if you do find the name but not the company, then fill the company with "N.A"
    """
    
    prompt = prompt_template.format(context=text_first_page, query=query)

    # Execute the prompt with the LLM
    response = llm(prompt)
    
    if(str(response.content).lower() == "not found"):
        prompt = prompt_template.format(context=text_second_page, query=query)
        response = llm(prompt)

    policy_string = str(response.content)
    policy_dict = {}
    for line in policy_string.strip().split('\n'):
        key, value = line.split(':', 1)
        key = key.strip()
        value = value.strip()
        policy_dict[key] = value

    print(policy_dict["Name of Policy"])
    if(policy_dict["Name of Policy"]):
        pinecone_index_name = get_index_name_by_policy_name(policy_dict["Name of Policy"])
        if(pinecone_index_name == None):
            st.write("The policy is yet to be uploaded, not a part of our policies")
            return None
        else:
            return pinecone_index_name
    else:
        st.write("policy's Name couldnt be found ")
        return None
    
    # Print the response
    
    
    # prompt_template = """Write a short summary of this Insurance document. 

    # You should Only Output in the following format
    # Name of the Insurance: 
    # Type of Insurance: ex. health, car etc
    # Providing Company of the Insurance:
    
    # These details will definetely be there in the text that you are summarising , please look carefully for this

    # {text}

    # SUMMARY:"""
    # PROMPT = PromptTemplate(template=prompt_template, input_variables=["text"])
    # chain = load_summarize_chain(llm, chain_type="map_reduce", 
    #                             map_prompt=PROMPT, combine_prompt=PROMPT)
    # summary_output = chain({"input_documents": [doc]},return_only_outputs=True)["output_text"]
    # # Check if text was extracted
    # return summary_output
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
    chunk_overlap=100,
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
            pineconeIndex = Name_and_details_extract(uploaded_file,llm)
            st.session_state.index_name = pineconeIndex
            if(pineconeIndex != None):
                summary = get_summary_by_index_name(pineconeIndex)
                st.write(f"Here is a quick summary of your insurance policy: {file_name}: {summary}")

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