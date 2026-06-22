import pdfplumber
from google import genai
from google.genai import types
import pandas as pd
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Gemini Client setup
client = genai.Client()

def extract_text_from_file(file_file):
    """Alag-alag files (PDF, CSV, Excel, TXT) se text nikalne ka function"""
    file_name = file_file.name.lower()
    
    # 1. Agar PDF file hai
    if file_name.endswith('.pdf'):
        with pdfplumber.open(file_file) as pdf:
            return "".join([page.extract_text() or "" for page in pdf.pages])
            
    # 2. Agar CSV file hai
    elif file_name.endswith('.csv'):
        df = pd.read_csv(file_file)
        return df.to_string() # Table ko text format me badal raha hai
        
    # 3. Agar Excel (.xlsx) file hai
    elif file_name.endswith('.xlsx'):
        df = pd.read_excel(file_file)
        return df.to_string()
        
    # 4. Agar normal Text (.txt) file hai
    elif file_name.endswith('.txt'):
        return file_file.read().decode("utf-8")
        
    else:
        raise ValueError("Unsupported file format!")

def extract_details_with_ai(text, columns):
    """Gemini API ke zariye structured data nikalne ka function"""
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
