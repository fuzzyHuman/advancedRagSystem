import streamlit as st
from PyPDF2 import PdfReader # type: ignore
from langchain.chains import load_summarize_chain
from langchain import PromptTemplate

def summarize_first_page(uploaded_file, llm):
    # Read the first page of the PDF content
    pdf = PdfReader(uploaded_file)
    first_page = pdf.pages[0]
    text = first_page.extract_text()

    prompt_template = """Write a short summary of this document. 

    You should Only Output in the following format
    Name of the Insurance

    {text}

    SUMMARY:"""
    PROMPT = PromptTemplate(template=prompt_template, input_variables=["text"])
    chain = load_summarize_chain(llm, chain_type="map_reduce", 
                                map_prompt=PROMPT, combine_prompt=PROMPT)
    summary_output = chain({"input_documents": docs},return_only_outputs=True)["output_text"]
    # Check if text was extracted
    if not text:
        return "No text could be extracted from the first page."

    # Custom prompt to guide the summarization
    custom_prompt = f"Summarize the following text from the first page succinctly: {text}"

    # Load the summarization chain with custom prompt handling
    chain = load_summarize_chain(llm, prompt_template=custom_prompt)

    # Get the summary
    summary = chain.run(text)
    return summary

def one_page_summary_service():
    st.sidebar.subheader("Upload PDF for One-Page Summary")

    # Upload file
    uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file:
        llm = st.session_state.llm  # Assuming LLM is stored in session state
        summary = summarize_first_page(uploaded_file, llm)
        st.sidebar.write(f"Summary of the first page: {summary}")
