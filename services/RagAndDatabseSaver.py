import os
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Pinecone as langPinecone
from dotenv import load_dotenv
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from langchain_openai import AzureChatOpenAI
from langchain import PromptTemplate
from databaseRetrieval import save_policy_details,save_summary_as_quick_summary
from customSummarisation import summarize_insurance_document
import uuid

def Name_and_details_extract(file_path, llm):
    # Load the PDF file
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    # Extract text from the first and second pages
    if len(documents) < 2:
        raise ValueError("The PDF does not contain enough pages to extract information.")

    text_first_page = documents[0].page_content
    text_second_page = documents[1].page_content

    # Define the prompt template
    prompt_template = PromptTemplate(
        input_variables=["context", "query"],
        template="""
        Context: {context}
        
        Query: {query}
        
        Answer:
        """
    )
    
    query = """given is the summary page of an Insurance Policy, give me an output in the following form, stick to keeping the name of key same i.e keep Name of Policy key as it is, dont add anythong else:
    
    Name of Policy: 
    Providing Company of the Policy: 
    
    if you don't find Name of the policy, only respond as "not found", if you do find the name but not the company, then fill the company with "N.A"
    """
    
    prompt = prompt_template.format(context=text_first_page, query=query)
    
    # Execute the prompt with the LLM
    response = llm(prompt)
    
    if str(response.content).lower() == "not found":
        prompt = prompt_template.format(context=text_second_page, query=query)
        response = llm(prompt)

    policy_string = str(response.content)
    policy_dict = {}
    for line in policy_string.strip().split('\n'):
        key, value = line.split(':', 1)
        policy_dict[key.strip()] = value.strip()

    print(policy_dict)
    
    # Generate a UUID for the index name
    index_name = str(uuid.uuid4())
    policy_dict["index_name"] = index_name
    
    
    if policy_dict:
        save_policy_details(policy_dict)
    
    # Return the UUID as the index name
    return index_name

# Initialize the language model
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

# Create RAG and save embeddings in Pinecone
def create_rag_and_save(file_path, index_name):
    load_dotenv()
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=4)
    docs = text_splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings()

    client = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
    
    # Check and create the index if it doesn't exist
    if index_name not in client.list_indexes().names():
        client.create_index(name=index_name, metric="cosine", dimension=768, spec=ServerlessSpec(cloud="aws", region="us-east-1"))

        docsearch = langPinecone.from_documents(docs, embeddings, index_name=index_name)

# Main function to process all PDFs in the specified folder
def process_all_pdfs_in_folder(folder_path):
    llm = initialize_llm()
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            index_name = Name_and_details_extract(file_path, llm)
            create_rag_and_save(file_path, index_name)
            summary = summarize_insurance_document(index_name)
            save_summary_as_quick_summary(index_name,summary)

# Define the folder containing the PDF files
pdf_folder_path = ("/Users/flam-flam/Documents/GitHub/advancedRagSystem/Insurance_pdf")

# Process all PDF files in the folder
process_all_pdfs_in_folder(pdf_folder_path)
