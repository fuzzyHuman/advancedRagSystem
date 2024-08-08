import streamlit as st
from services.pdfUploadService import upload_pdf_service
from services.queryService import process_user_query
from services.onePageSummary import one_page_summary_service

# Handler to process user query and update conversation history
def process_query():
    user_input = st.session_state.user_input
    if user_input:
        # Process the user query and get the response
        response = process_user_query(user_input)
        
        # Update the conversation history
        st.session_state.conversation_history.append({"query": user_input, "response": response})
        
        # Clear the input box by setting user_input to an empty string
        st.session_state.user_input = ""

# Main Application
def main():
    st.title("Insurance Expert")
    st.write("Welcome to the Insurance Expert app. How can I assist you today?")

    # Initialize session state for conversation history
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []

    # Input box for user prompts with an on_change handler
    st.text_input("Enter your query:", key="user_input", on_change=process_query)

    # Display the conversation history
    if st.session_state.conversation_history:
        for entry in st.session_state.conversation_history:
            st.write(f"**You:** {entry['query']}")
            st.write(f"**App:** {entry['response']}")
            st.write("---")

    # Call the PDF upload service in the sidebar
    upload_pdf_service()

if __name__ == "__main__":
    main()