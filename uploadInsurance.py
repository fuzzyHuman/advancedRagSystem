import streamlit as st
from supabase import create_client, Client
import os

# Supabase credentials
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


# Streamlit UI for file upload
st.title("Upload a PDF File")

uploaded_file = st.file_uploader("Choose a   PDF file", type="pdf")

if uploaded_file is not None:
    # Save the file to the server
    file_details = {"filename": uploaded_file.name, "filetype": uploaded_file.type, "filesize": uploaded_file.size}
    st.write(file_details)

    # Read the file content
    content = uploaded_file.read()

    # Upload to Supabase
    res = supabase.storage.from_('your_bucket_name').upload(uploaded_file.name, content)
    if res.status_code == 200:
        st.success("File uploaded successfully!")
    else:
        st.error("Failed to upload the file.")