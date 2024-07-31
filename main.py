from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain.document_loaders import TextLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Pinecone as langPinecone
from pinecone.grpc import PineconeGRPC as Pinecone
from dotenv import load_dotenv
from pinecone import ServerlessSpec
from langchain_openai import AzureChatOpenAI
#import pinecone
import os


class ChatBot():
    load_dotenv()
    loader = PyPDFLoader("Insurance1.pdf")
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=4)
    docs = text_splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings()

    client = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
   
    # Define Index Name
    index_name = "langchain-demo"

    # Checking Index
    if index_name not in client.list_indexes().names():
        # Create new Index
        client.create_index(name=index_name, metric="cosine", dimension=768,spec=ServerlessSpec(cloud="aws",region="us-east-1"))
        docsearch = langPinecone.from_documents(docs, embeddings, index_name=index_name)
    else:
        # Link to the existing index
        docsearch = langPinecone.from_existing_index(index_name, embeddings)
        
        
    # from langchain.llms import HuggingFaceHub

    # Define the repo ID and connect to Mixtral model on Huggingface
    repo_id = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    
    model = AzureChatOpenAI(
        openai_api_key = os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
        deployment_name = "gpt-4",
        model = "gpt-4",
        temperature=0.3,
        openai_api_version = "2024-02-01",
    )
    # llm = HuggingFaceHub(
    # repo_id=repo_id, 
    # model_kwargs={"temperature": 0.8, "top_k": 50}, 
    # huggingfacehub_api_token=os.getenv('HUGGINGFACE_API_KEY')
    # )
    llm = model
    from langchain import PromptTemplate

    template = """
    You are a question answer agents. These Human will ask you a question 
    Use following piece of context to answer the question. 
    If you don't know the answer, just say you don't know. 
    Keep the answer within 2 sentences and concise.

    Context: {context}
    Question: {question}
    Answer: 

    """

    prompt = PromptTemplate(
    template=template, 
    input_variables=["context", "question"]
    )

    from langchain.schema.runnable import RunnablePassthrough
    from langchain.schema.output_parser import StrOutputParser

    rag_chain = (
    {"context": docsearch.as_retriever(),  "question": RunnablePassthrough()} 
    | prompt 
    | llm
    | StrOutputParser() 
    )
    
load_dotenv()  
bot = ChatBot()
input = input("Ask me anything: ")
result = bot.rag_chain.invoke(input)
print(result)



