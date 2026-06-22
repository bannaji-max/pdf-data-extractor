import pdfplumber
from google import genai
from google.genai import types
import json
import os
from dotenv import load_dotenv

# .env file se API Key load karne ke liye
load_dotenv()

# Gemini Client setup (Yeh automatically GEMINI_API_KEY environment variable check karega)
client = genai.Client()

def extract_text_from_pdf(pdf_file):
    """PDF se text nikalne ka function"""
    with pdfplumber.open(pdf_file) as pdf:
        return "".join([page.extract_text() or "" for page in pdf.pages])

def extract_details_with_ai(text, columns):
    """Gemini API ke zariye structured data nikalne ka function"""
    prompt = f"""
    Analyze the following document text and extract data for these columns: {', '.join(columns)}.
    Return the output strictly as a JSON object with a main key named "data", which contains a list of objects.
    Example format: {{"data": [{{"Name": "John", "Phone": "1234"}}]}} If a value is missing, use null.
    
    Text:
    {text}
    """
    
    # Gemini 2.5 Flash model ka use kar rahe hain jo fast aur free tier me available hai
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )
    
    return json.loads(response.text)
