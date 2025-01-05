import streamlit as st
import pandas as pd
from openai import OpenAI
import os
import json
import time
from datetime import datetime
from PIL import Image

os.environ['OPENAI_API_KEY'] = 'your-api-key'
OpenAI.api_key = os.getenv('OPENAI_API_KEY')

# Set up OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Streamlit App UI
st.title("AI-Powered Data Visualization App")
st.write("Upload a CSV or Excel file, enter your query, and let AI create the visualization for you.")

# File upload
uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])

# User query input
user_query = st.text_input("Enter your query for visualization (e.g., 'Visualize revenue by year')")


# Process the uploaded file
if uploaded_file:
    # Load data into a DataFrame
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    st.write("### Uploaded Data Preview:")
    st.dataframe(df.head())

    unique_json_path = f"fin_data_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    json_data = df.to_json(orient="columns")

    with open(unique_json_path, "w") as json_file:
        json.dump(json_data, json_file)

    # Upload file to OpenAI
    file = client.files.create(
        file=open(unique_json_path, "rb"),
        purpose='assistants'
    )

