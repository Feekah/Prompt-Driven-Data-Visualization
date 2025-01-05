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
