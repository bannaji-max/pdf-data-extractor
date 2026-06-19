import pdfplumber
from openai import OpenAI
import json
import os
from dotenv import load_dotenv

# .env फाइल से API Key लोड करने के लिए
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_text_from_pdf(pdf_file):
    """PDF से टेक्स्ट निकालने का फंक्शन"""
    with pdfplumber.open(pdf_file) as pdf:
        return "".join([page.extract_text() or "" for page in pdf.pages])

def extract_details_with_ai(text, columns):
    """OpenAI API के जरिए विशिष्ट डेटा निकालने का फंक्शन"""
    prompt = f"""
    Analyze the following document text and extract data for these columns: {', '.join(columns)}.
    Return the output strictly as a JSON object with a main key named "data", which contains a list of objects.
Example format: {"data": [{"Name": "John", "Phone": "1234"}]} If a value is missing, use null.
    
    Text:
    {text}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(response.choices[0].message.content)
