from langchain_openai import AzureChatOpenAI
import os
from services.databaseRetrieval import get_all_summaries_with_index_names,get_policy_name_by_index_name
import streamlit as st
import dotenv
import requests

def initialize_llama_model():
    """
    Initialize LLaMA model with GCP endpoint and authorization headers.
    Parameters:
        - None
    Returns:
        - tuple: A tuple containing the API URL (str) and headers (dict).
    Example:
        - initialize_llama_model() -> ("https://example-endpoint/v1beta1/projects/project-id/locations/region/endpoints/openapi/chat/completions", {"Authorization": "Bearer access_token", "Content-Type": "application/json"})
    """
    endpoint = os.getenv("GCP_AI_ENDPOINT")
    region = os.getenv("GCP_REGION")
    project_id = os.getenv("GCP_PROJECT_ID")
    
    api_url = f"https://{endpoint}/v1beta1/projects/{project_id}/locations/{region}/endpoints/openapi/chat/completions"
    access_token = os.popen('AIzaSyBGF3007pngZ4KS1-YbuDGUl6tHAn0DpfI').read().strip()

    headers = {
        "Authorization": f"Bearer AIzaSyBGF3007pngZ4KS1-YbuDGUl6tHAn0DpfI",
        "Content-Type": "application/json"
    }

    return api_url, headers

def llama_chat_completion(api_url, headers, prompt):
    payload = {
        "model": "meta/llama3-405b-instruct-maas",
        "stream": True,  # Adjust based on your needs
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(api_url, headers=headers, json=payload)
    response.raise_for_status()
    
    return response.json()  # Or process the streamed response accordingly

def getLlamaResponse(prompt):
    api_url,headers = initialize_llama_model()
    return llama_chat_completion(api_url,headers,prompt)


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
def score_policy_explanation_with_llm(explanation, summaries_with_index_names):
    llm = initialize_llm()
    
    max_score = -1
    best_policy_name = ""

    for policy in summaries_with_index_names:
        index_name = policy["index_name"]
        summary = policy["summary"]

        # Create the structured prompt
        prompt = f"""
        You are an expert in insurance policies. I will provide you with two pieces of text: 
        1. A summary of an insurance policy.
        2. A user's explanation of the insurance policy they are looking for.

        Your task is to determine how well the user's explanation matches the provided policy summary. 
        Please evaluate the similarity and relevance on a scale of 1 to 10, where 1 means "not related at all" 
        and 10 means "perfectly matches."

        Here is the policy summary:

        Policy Summary: "{summary}"

        Here is the user's explanation:

        User Explanation: "{explanation}"

        Please provide a score out of 10 and explain why you chose this score.
        
        score should be in the first line and nothing else should be there in the first line. 
        """

        # Get the response from the LLM
        response = llm(prompt)
        llamaResponse = getLlamaResponse(prompt)
        print(llamaResponse)
        
        # Extract the score from the response
        try:
            score_line = str(response.content).strip().split('\n')[0]  # Assuming score is in the first line
            score = float(score_line.split()[-1])
        except Exception as e:
            print(f"Failed to parse score: {e}")
            continue
        
        # Update the max score and best policy name
        if score > max_score:
            max_score = score
            best_policy_name = index_name

    return best_policy_name

def find_best_policy(explanation):
    # Retrieve all summaries with their associated index names
    summaries_with_index_names = get_all_summaries_with_index_names()
    
    # Score the policy explanation against all summaries
    best_policy_name = score_policy_explanation_with_llm(explanation, summaries_with_index_names)
    
    return best_policy_name

def display_insurance_comparison_app():
    dotenv.load_dotenv()
    # st.title("Insurance Policy Comparison App")

    # Use the sidebar for the insurance comparison tool
    with st.sidebar:
        st.header("Please input what kind of insurance policy are you looking for?")
        # Display the text box in the sidebar
        user_input = st.text_area("Describe your desired insurance policy", height=200)

        if st.button("Find Best Policy"):
            if user_input:
                # Process the user input and find the best matching policy
                best_policy = find_best_policy(user_input)
                name_of_best_policy = get_policy_name_by_index_name(best_policy)
                st.success(f"The best matching policy is: {name_of_best_policy}")
            else:
                st.warning("Please enter a description of your desired insurance policy.")