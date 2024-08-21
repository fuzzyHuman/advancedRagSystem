from langchain_openai import AzureChatOpenAI
import streamlit as st
from PyPDF2 import PdfReader # type: ignore
from langchain.chains import load_summarize_chain
from langchain import PromptTemplate
import os
from langchain_core.documents import Document

def summarize_first_page(uploaded_file, llm):
    # Read the first page of the PDF content
    pdf = PdfReader(uploaded_file)
    first_page = pdf.pages[0]
    second_page = pdf.pages[1]
    
    text_first_page = first_page.extract_text()
    text_second_page = second_page.extract_text()
    doc1 = Document(page_content=text_first_page)
    doc2 = Document(page_content=text_second_page)
    
    prompt_template = PromptTemplate(
    input_variables=["context", "query"],
    template="""
    Context: {context}
    
    Query: {query}
    
    Answer:
    """
    )
    query = """given is the text of first page of an Insurance Policy , give me an output in the following form:
    
    Name of Policy: 
    Type of Policy:
    Providing Company of the Policy: 
    
    """
    prompt = prompt_template.format(context=text, query=query)

    # Execute the prompt with the LLM
    response = llm(prompt)

    # Print the response
    print(response)
    return response.content
    
    
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
def one_page_summary_service():
    st.sidebar.subheader("Upload PDF for One-Page Summary")

    # Upload file
    uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file:
        llm = initialize_llm()  # Assuming LLM is stored in session state
        summary = summarize_first_page(uploaded_file, llm)
        st.sidebar.write(f"Summary of the first page: {summary}")
