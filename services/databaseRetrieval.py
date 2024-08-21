from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import uuid

# MongoDB connection URI
uri = "mongodb+srv://sharmasudeepiit:KUk2sppvfdIgjLpv@insurancedetails.coenc.mongodb.net/?retryWrites=true&w=majority&appName=InsuranceDetails"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Access the database and collection
db = client['InsuranceDetails']
collection = db['paramSummary']
answers_collection = db['policyAnswers']

def save_policy_details(policy_details):
    # Insert the policy details into the collection
    result = collection.insert_one(policy_details)
    print(f"Inserted document with ID: {result.inserted_id}")

def get_index_name_by_policy_name(policy_name):
    # Find the document with the given policy name
    document = collection.find_one({"Name of Policy": policy_name}, {"_id": 0, "index_name": 1})
    if document:
        return document.get("index_name")
    else:
        return None
    
def save_summary_as_quick_summary(index_name, summary_dict):
    # Format the summary string
    summary_string = "\n".join(answer for question, answer in summary_dict.items())
    
    # Update the document with the new Quick Insurance summary field
    result = collection.update_one(
        {"index_name": index_name},
        {"$set": {"Quick Insurance summary": summary_string}}
    )
    
    if result.modified_count > 0:
        print(f"Updated document with index name: {index_name}")
    else:
        print(f"No document found with index name: {index_name}")
        
def get_summary_by_index_name(index_name):
    # Find the document with the given index name
    document = collection.find_one({"index_name": index_name}, {"_id": 0, "Quick Insurance summary": 1})
    if document:
        return document.get("Quick Insurance summary")
    else:
        return None
    
def save_policy_answer(index_name, question, answer):
    # Generate a unique ID for the question-answer pair
    qa_id = str(uuid.uuid4())
    
    # Prepare the question-answer pair document
    qa_pair = {
        "id": qa_id,
        "question": question,
        "answer": answer
    }
    
    # Update the document with the new question and answer pair
    result = answers_collection.update_one(
        {"index_name": index_name},
        {"$push": {"qa_pairs": qa_pair}},
        upsert=True
    )
    
    if result.upserted_id:
        print(f"Inserted new document with index name: {index_name}")
    elif result.modified_count > 0:
        print(f"Updated document with index name: {index_name}")
    else:
        print(f"No changes made to the document with index name: {index_name}")

def get_policy_questions(index_name):
    # Retrieve all questions for the given index_name from the collection
    document = answers_collection.find_one({"index_name": index_name}, {"_id": 0, "qa_pairs": 1})
    questions = []
    if document:
        qa_pairs = document.get("qa_pairs", [])
        for qa in qa_pairs:
            questions.append({"id": qa["id"], "question": qa["question"]})
    return questions
def get_answer_for_policy_question(index_name, question):
    # Retrieve the answer for the given question and index_name
    document = answers_collection.find_one({"index_name": index_name, "qa_pairs.question": question}, {"_id": 0, "qa_pairs.$": 1})
    if document:
        return document["qa_pairs"][0]["answer"]
    else:
        return None
    
def get_answer_by_index_and_id(index_name, qa_id):
    # Retrieve the answer for the given index_name and QnA ID
    document = answers_collection.find_one({"index_name": index_name, "qa_pairs.id": qa_id}, {"_id": 0, "qa_pairs.$": 1})
    if document:
        return document["qa_pairs"][0]["answer"]
    else:
        return None
    
def get_all_index_names():
    # Retrieve all unique index names from the paramSummary collection
    index_names = collection.distinct("index_name")
    return index_names

def get_all_summaries_with_index_names():
    # Retrieve all documents with their index names and summaries
    documents = collection.find({}, {"_id": 0, "index_name": 1, "Quick Insurance summary": 1})
    
    summaries_with_index_names = []
    
    for doc in documents:
        index_name = doc.get("index_name")
        summary = doc.get("Quick Insurance summary", "")
        summaries_with_index_names.append({"index_name": index_name, "summary": summary})
    
    return summaries_with_index_names