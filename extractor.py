import pdfplumber
from google import genai
from google.genai import types
import pandas as pd
import json
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client()

def extract_text_from_file(file_file):
    file_name = file_file.name.lower()
    if file_name.endswith('.pdf'):
        with pdfplumber.open(file_file) as pdf:
            return "".join([page.extract_text() or "" for page in pdf.pages])
    elif file_name.endswith('.csv'):
        df = pd.read_csv(file_file)
        return df.to_string()
    elif file_name.endswith('.xlsx'):
        df = pd.read_excel(file_file)
        return df.to_string()
    elif file_name.endswith('.txt'):
        return file_file.read().decode("utf-8")
    else:
        raise ValueError("Unsupported file format!")

def detect_columns_with_ai(text):
    prompt = f"""
    Analyze the following document text and identify all the possible column names, headers, or fields available in it.
    Return the output strictly as a JSON object with a single key named "detected_columns", which contains a list of strings (the column names).
    Example format: {{"detected_columns": ["Name", "Age", "Salary"]}}
    
    Text:
    {text}
    """
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )
    result = json.loads(response.text)
    return result.get("detected_columns", [])

def extract_details_with_ai(text, columns):
    prompt = f"""
    Analyze the following document text and extract data for these columns: {', '.join(columns)}.
    Return the output strictly as a JSON object with a main key named "data", which contains a list of objects.
    Example format: {{"data": [{{"Name": "John", "Phone": "1234"}}]}} If a value is missing, use null.
    
    Text:
    {text}
    """
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )
    return json.loads(response.text)
