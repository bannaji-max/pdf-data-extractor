import streamlit as st
import pandas as pd
import io
from extractor import extract_text_from_file, detect_columns_with_ai, extract_details_with_ai

# Page Config with modern layout
st.set_page_config(page_title="DataExtract AI", page_icon="⚡", layout="centered")

# Custom CSS for Modern SaaS UI Look
st.markdown("""
    <style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Title Styling */
    .main-title {
        font-size: 2.8rem;
        font-weight: 700;
        letter-spacing: -0.03em;
        background: linear-gradient(90deg, #ff4b4b 0%, #ff8585 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        color: #808495;
        font-size: 1.1rem;
        margin-bottom: 2.5rem;
    }
    
    /* Elegant Cards / Container Boxes */
    div[data-testid="stForm"], .stMarkdown div {
        border-radius: 16px;
    }
    
    /* Modern Input Styling */
    .stTextInput col {
        border-radius: 10px;
    }
    
    /* Primary Buttons Styling */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #ff4b4b 0%, #e63946 100%);
        color: white;
        border: none;
        padding: 0.6rem 2rem;
        border-radius: 12px;
        font-weight: 600;
        letter-spacing: -0.01em;
        box-shadow: 0 4px 14px rgba(255, 75, 75, 0.3);
        transition: all 0.3s ease;
        width: 100%;
    }
    
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 75, 75, 0.4);
        background: linear-gradient(135deg, #ff5e5e 0%, #ff4b4b 100%);
    }
    
    /* Download Button (Secondary/Success) */
    div[data-testid="stDownloadButton"] > button {
        background-color: #2ec4b6 !important;
        color: white !important;
        border: none !important;
        padding: 0.6rem 2rem !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 14px rgba(46, 196, 182, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    div[data-testid="stDownloadButton"] > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(46, 196, 182, 0.4) !important;
    }
    
    /* File Uploader styling wrapper */
    .uploadedFile {
        border-radius: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# Custom Header HTML for beautiful look
st.markdown('<h1 class="main-title">⚡ DataExtract AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Instantly transform any document into a structured Excel sheet powered by Gemini 2.5</p>', unsafe_allow_html=True)

# File Uploader Container
uploaded_file = st.file_uploader("Upload Document (PDF, CSV, XLSX, TXT)", type=["pdf", "csv", "xlsx", "txt"])

if uploaded_file:
    if "current_file" not in st.session_state or st.session_state.current_file != uploaded_file.name:
        with st.spinner("✨ AI is analyzing document structure..."):
            try:
                text = extract_text_from_file(uploaded_file)
                st.session_state.file_text = text
                st.session_state.detected_cols = detect_columns_with_ai(text)
                st.session_state.current_file = uploaded_file.name
            except Exception as e:
                st.error(f"Error reading file: {e}")
                st.session_state.detected_cols = []

    if st.session_state.detected_cols:
        st.write("---")
        # Multiselect Dropdown
        selected_columns = st.multiselect(
            "📋 Select headings/columns to extract:",
            options=st.session_state.detected_cols,
            default=st.session_state.detected_cols
        )
        
        if selected_columns:
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            if st.button("🚀 Extract & Structured Data"):
                with st.spinner("⏳ Compiling data into tables..."):
                    try:
                        raw_data = extract_details_with_ai(st.session_state.file_text, selected_columns)
                        
                        if "data" in raw_data:
                            data = raw_data["data"]
                        else:
                            key = list(raw_data.keys())[0] if raw_data.keys() else None
                            data = raw_data[key] if key and isinstance(raw_data[key], list) else [raw_data]

                        df = pd.DataFrame(data)
                        
                        # Fix: 0 se counting hata kar 1 se shuru karne ke liye
                        df.index = df.index + 1
                        
                        st.write("---")
                        st.subheader("🎯 Preview Results")
                        st.dataframe(df, use_container_width=True)
                        
                        buffer = io.BytesIO()
                        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                            df.to_excel(writer, index=False)
                        
                        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
                        st.download_button(
                            label="📥 Download Excel Sheet",
                            data=buffer.getvalue(),
                            file_name="extracted_data.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    except Exception as e:
                        st.error(f"Error extracting data: {e}")
        else:
            st.warning("Please select at least one column to proceed.")
    else:
        st.warning("AI could not detect columns. Please upload a clearer document.")
