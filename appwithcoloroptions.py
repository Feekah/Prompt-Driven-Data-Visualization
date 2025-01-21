import streamlit as st
import pandas as pd
from openai import OpenAI
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from PIL import Image

load_dotenv()
api_key = os.getenv('OPENAI_KEY')

# Set up OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_KEY"))

# Streamlit App UI
st.title("AI-Powered Data Visualization App")
st.write("Upload a CSV or Excel file, enter your query, and let AI create the visualization for you.")

# File upload
uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])

# User query input
user_query = st.text_input("Enter your query for visualization (e.g., 'Visualize revenue by year')")

# Color theme selection
color_theme = st.selectbox("Select a color theme for your visualization", 
                           ["Fiery Red", "Executive Blue", "Monochrome"])

# Define color palettes for each theme
color_palettes = {
    #"Fiery Red": ["#FF4500", "#FFA500", "#FFD700"],  # Reds, oranges, golds
    "Fiery Red": ["Red", "Orange", "Yellow"],
    "Executive Blue": ["Blue", "White", "Black"],  # Dark blue, black, white
    "Monochrome": ["Black", "White", "Grey"],  # Yellow, black, white
}

# Check if a file has been uploaded
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

    # Include color palette in the instructions for the assistant
    color_instructions = f"Use the following color palette for the visualization: {', '.join(color_palettes[color_theme])}"

    # Define assistant instructions
    assistant = client.beta.assistants.create(
        instructions=f"You are a data scientist assistant. When given data, a query, and a color palette, write the proper code and create the proper visualization based on the query. " + color_instructions,
        model="gpt-4o",
        tools=[{"type": "code_interpreter"}],
        tool_resources={"code_interpreter": {"file_ids": [file.id]}}
    )

    # Create a thread and send the user query
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": user_query
            }
        ]
    )

    # Run the assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    st.write("Generating plot...")

    # Check for completion and retrieve the plot
    while True:
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        try:
            # Check if image file is in response
            plot_file_id = messages.data[0].content[0].image_file.file_id
            time.sleep(5)  # Wait a bit to ensure run is completed
            break
        except:
            time.sleep(5)
            st.write("Assistant is still processing...")

    # Retrieve and display the plot
    def convert_file_to_png(file_id, write_path):
        data = client.files.content(file_id)
        data_bytes = data.read()
        with open(write_path, "wb") as file:
            file.write(data_bytes)

    # Convert plot to PNG and display
    image_path = "generated_plot.png"
    convert_file_to_png(plot_file_id, image_path)
    
    st.write("### Generated Plot:")
    st.image(image_path)

    # Clean up temporary files
    os.remove(unique_json_path)
    os.remove(image_path)
