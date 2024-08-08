from databaseRetrieval import save_policy_answer,get_all_index_names

def save_policy_questions(index_name):
    questions = [
        "What are the types of plans available?",
        "What is the extent of coverage provided by the policy?",
        "Does it cover hospital stays, surgeries, doctor visits, prescription drugs, and emergency care?",
        "Are there any exclusions or limitations?",
        "Does the policy cover pre-existing conditions?",
        "If yes, is there a waiting period before coverage begins?",
        "What is the network of healthcare providers?",
        "Are my preferred doctors and hospitals included in the network?",
        "Are specialist consultations covered?",
        "Do I need a referral from a primary care physician?",
        "What is the premium amount?",
        "How often do I need to pay it (monthly, quarterly, annually)?",
        "What is the deductible?",
        "How much do I need to pay out-of-pocket before the insurance starts covering expenses?",
        "What are the co-payments and co-insurance amounts?",
        "What percentage of the costs will I be responsible for after meeting the deductible?",
        "What is the out-of-pocket maximum?",
        "What is the maximum amount I will have to pay in a policy year?",
        "Does the policy include wellness programs?",
        "Are there incentives for participating in health and wellness activities?",
        "Are preventive services covered?",
        "Such as vaccinations, screenings, and annual check-ups.",
        "Are mental health services covered?",
        "What kind of coverage is provided for therapy, counseling, and psychiatric services?",
        "Does the policy offer maternity and newborn care?",
        "What is the extent of coverage for prenatal and postnatal care?",
        "Are alternative treatments covered?",
        "Such as acupuncture, chiropractic care, and physiotherapy.",
        "Does the policy cover dental and vision care?",
        "Are there options to add these coverages if not included?",
        "Are prescription drugs covered?",
        "Are there specific drugs that are excluded or require prior authorization?",
        "Are there any rewards or discounts for maintaining a healthy lifestyle?",
        "How are these rewards measured and provided?",
        "Does the policy include a fitness program or gym membership reimbursement?",
        "What are the criteria to qualify for such benefits?",
        "Are there health tracking tools or apps provided by the insurer?",
        "How do these tools integrate with the policy and rewards system?",
        "How is the claims process handled?",
        "Is it straightforward and user-friendly?",
        "What is the turnaround time for claim approvals and reimbursements?",
        "Is there a 24/7 customer service helpline?",
        "How accessible and responsive is the customer service team?",
        "What are the terms and conditions for policy renewal?",
        "Is there a possibility of premium increases?",
        "Is the policy portable if I move to a different state or country?",
        "What are the procedures and conditions for portability?",
        "What is the financial stability and reputation of the insurance company?",
        "What do customer reviews and ratings indicate about their service quality?",
        "How does the policy handle coverage for chronic conditions?",
        "What kind of support and coverage can I expect for ongoing treatments?",
        "What happens if I need treatment abroad?",
        "Does the policy cover international medical expenses?",
        "Are there options to customize the policy with additional riders?",
        "Such as critical illness cover, accidental death benefit, etc.",
        "Can the sum insured be enhanced during the policy tenure?",
        "What are the conditions and procedures for increasing coverage?",
        "Is the policy compliant with local health insurance regulations?",
        "Are there any tax benefits associated with purchasing this policy?"
    ]

    
    # Save each question with an empty answer
    for question in questions:
        save_policy_answer(index_name, question, "")
        
index_names = get_all_index_names()
# Loop through each index name and save the policy questions with empty answers
for index_name in index_names:
    save_policy_questions(index_name)