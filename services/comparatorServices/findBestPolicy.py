from langchain_openai import AzureChatOpenAI
import os
from services.databaseRetrieval import get_all_summaries_with_index_names

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
        
        # Extract the score from the response
        try:
            score_line = response.strip().split('\n')[0]  # Assuming score is in the first line
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