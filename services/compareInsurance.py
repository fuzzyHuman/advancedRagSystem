import streamlit as st
from PyPDF2 import PdfReader
from langchain.chains import load_retrieve_and_generate_chain
from langchain_openai import AzureChatOpenAI
import os

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

# Function to extract text from a PDF
def extract_text_from_pdf(uploaded_file):
    pdf = PdfReader(uploaded_file)
    text = ""
    for page in pdf.pages:
        text += page.extract_text() or ""
    return text

# Function to compare two PDFs
def compare_health_policies(pdf1, pdf2, llm):
    text1 = extract_text_from_pdf(pdf1)
    text2 = extract_text_from_pdf(pdf2)

    # Define the sections to focus the comparison
    sections = ["Diseases Covered", "Cost", "Benefits Included", "Payment Options"]
    comparisons = {}

    for section in sections:
        prompt = f"Compare the section '{section}' between two health insurance policies:\n\nPolicy A: {text1}\n\nPolicy B: {text2}"
        chain = load_retrieve_and_generate_chain(llm, prompt_template=prompt)
        comparison_result = chain.run("")
        comparisons[section] = comparison_result

    return comparisons

def compare_policies_service():
    st.sidebar.subheader("Compare Health Insurance Policies")
    
    # Upload two PDF files
    pdf1 = st.sidebar.file_uploader("Upload first Health Insurance Policy PDF", type="pdf", key="pdf1")
    pdf2 = st.sidebar.file_uploader("Upload second Health Insurance Policy PDF", type="pdf", key="pdf2")
    
    if pdf1 and pdf2:
        llm = initialize_llm()
        comparison_results = compare_health_policies(pdf1, pdf2, llm)
        for section, result in comparison_results.items():
            st.write(f"### {section}")
            st.write(result)
