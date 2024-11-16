import streamlit as st
import openai
import requests
import pandas as pd
import matplotlib.pyplot as plt
import docx2txt
import pdfplumber
import csv
from bs4 import BeautifulSoup
from io import StringIO, BytesIO

# Set up OpenAI and Claude AI API keys
openai.api_key = st.text_input('Enter your OpenAI API Key', type='password')
claude_api_key = st.text_input('Enter your Claude API Key', type='password')

# Function to extract text from different file types
def extract_text(file):
    if file.type == "text/plain":
        return file.read().decode("utf-8")
    elif file.type == "application/pdf":
        with pdfplumber.open(file) as pdf:
            return "\n".join([page.extract_text() for page in pdf.pages])
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return docx2txt.process(file)
    elif file.type == "text/csv":
        return file.getvalue().decode("utf-8")
    elif file.type == "text/html":
        soup = BeautifulSoup(file.read(), "html.parser")
        return soup.get_text()
    else:
        return None

# Function to analyze text using OpenAI API
def analyze_with_openai(text):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"{expected_action}: {text}",
        max_tokens=200
    )
    return response.choices[0].text.strip()

# Function to analyze text using Claude AI API
def analyze_with_claude(text):
    headers = {"Authorization": f"Bearer {claude_api_key}", "Content-Type": "application/json"}
    data = {"prompt": f"{expected_action}: {text}", "max_tokens": 200}
    response = requests.post("https://api.anthropic.com/v1/complete", headers=headers, json=data)
    return response.json().get("completion", "")

# Streamlit app layout
st.title("File Analysis Tool with OpenAI and Claude AI")
uploaded_file = st.file_uploader("Upload a file (txt, pdf, docx, csv, html)", type=["txt", "pdf", "docx", "csv", "html"])

expected_action = st.text_input('What do you want to do with the file? (e.g., summarize, analyze sentiment, extract key points)')

if uploaded_file is not None:
    # Extract text from the uploaded file
    text = extract_text(uploaded_file)
    if text:
        st.subheader("Extracted Text")
        st.text_area("", text, height=200)

        # Analyze the text with OpenAI
        st.subheader("Analysis with OpenAI")
        openai_result = analyze_with_openai(text)
        st.write(openai_result)

        # Analyze the text with Claude AI
        st.subheader("Analysis with Claude AI")
        claude_result = analyze_with_claude(text)
        st.write(claude_result)

        # Display some analysis results visually
        st.subheader("Visual Analysis")
        word_count = len(text.split())
        char_count = len(text)
        st.write(f"Word Count: {word_count}")
        st.write(f"Character Count: {char_count}")

        # Create a bar chart
        st.subheader("Word and Character Count Bar Chart")
        fig, ax = plt.subplots()
        ax.bar(["Words", "Characters"], [word_count, char_count])
        st.pyplot(fig)

        # Create a downloadable report
        st.subheader("Downloadable Report")
        report = f"OpenAI Analysis:\n{openai_result}\n\nClaude AI Analysis:\n{claude_result}\n\nWord Count: {word_count}\nCharacter Count: {char_count}"
        report_bytes = BytesIO(report.encode('utf-8'))
        st.download_button(label="Download Report", data=report_bytes, file_name="analysis_report.txt", mime="text/plain")
    else:
        st.error("Unsupported file type or error extracting text.")
