import pdfplumber
from openai import OpenAI
import json
import os
from dotenv import load_dotenv

# [span_0](start_span).env फाइल से API Key लोड करने के लिए[span_0](end_span)
[span_1](start_span)load_dotenv()[span_1](end_span)
[span_2](start_span)client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))[span_2](end_span)

def extract_text_from_pdf(pdf_file):
    [span_3](start_span)"""PDF से टेक्स्ट निकालने का फंक्शन"""[span_3](end_span)
    [span_4](start_span)with pdfplumber.open(pdf_file) as pdf:[span_4](end_span)
        [span_5](start_span)return "".join([page.extract_text() or "" for page in pdf.pages])[span_5](end_span)

def extract_details_with_ai(text, columns):
    [span_6](start_span)"""OpenAI API के जरिए विशिष्ट डेटा निकालने का फंक्शन"""[span_6](end_span)
    # NOTE: JSON example ke liye curly braces ko double {{ }} kiya hai taaki f-string error na de
    prompt = f"""
    Analyze the following document text and extract data for these columns: {', '.join(columns)}.
    Return the output strictly as a JSON object with a main key named "data", which contains a list of objects.
    Example format: {{"data": [{{"Name": "John", "Phone": "1234"}}]}} If a value is missing, use null.
    
    Text:
    {text}
    """
    [span_7](start_span)response = client.chat.completions.create([span_7](end_span)
        [span_8](start_span)model="gpt-4o-mini",[span_8](end_span)
        [span_9](start_span)response_format={"type": "json_object"},[span_9](end_span)
        [span_10](start_span)messages=[{"role": "user", "content": prompt}][span_10](end_span)
    )
    [span_11](start_span)return json.loads(response.choices[0].message.content)[span_11](end_span)
