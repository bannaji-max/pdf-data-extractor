import streamlit as st
import pandas as pd
import io
from extractor import extract_text_from_file, detect_columns_with_ai, extract_details_with_ai

# Page Configuration
st.set_page_config(page_title="DataExtract AI", page_icon="✨", layout="centered")

# Smooth & Aesthetic Custom CSS (Very friendly for eyes)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    /* Font family global override */
    html, body, [class*="css"], .stMarkdown {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    /* Smooth Background & App Layout padding */
    .main .block-container {
        padding-top: 3rem;
        padding-bottom: 3rem;
        max-width: 700px;
    }
    
    /* Modern minimalist header */
    .hero-title {
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.04em;
        background: linear-gradient(135deg, #3a86ff 0%, #8338ec 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    
    .hero-subtitle {
        color: #64748b;
        font-size: 1rem;
        font-weight: 400;
        margin-bottom: 2rem;
    }
    
    /* File Uploader Container Box styling */
    section[data-testid="stFileUploadDropzone"] {
        border: 2px dashed #cbd5e1 !important;
        border-radius: 16px !important;
        background-color: rgba(248, 250, 252, 0.6) !important;
        padding: 2rem !important;
        transition: all 0.3s ease;
    }
    
    section[data-testid="stFileUploadDropzone"]:hover {
        border-color: #3a86ff !important;
        background-color: rgba(241, 245, 249, 0.9) !important;
    }
    
    /* Premium Multi-select Tags customized styling */
    span[data-baseweb="tag"] {
        background-color: #e2e8f0 !important;
        color: #334155 !important;
        border-radius: 8px !important;
        padding: 4px 10px !important;
        font-weight: 500 !important;
    }
    
    /* Extract Button - Clean Soft Indigo Gradient */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.7rem 2rem !important;
        border-radius: 12px !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        letter-spacing: -0.01em !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2) !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        width: 100% !important;
        margin-top: 10px;
    }
    
    div.stButton > button:first-child:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(79, 70, 229, 0.35) !important;
        opacity: 0.95;
    }
    
    /* Download Button - Minimal Soft Emerald look */
    div[data-testid="stDownloadButton"] > button {
        background: #10b981 !important;
        color: white !important;
        border: none !important;
        padding: 0.6rem 1.8rem !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2) !important;
        transition: all 0.2s ease !important;
    }
    
    div[data-testid="stDownloadButton"] > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 16px rgba(16, 185, 129, 0.3) !important;
    }
    
    /* Custom divider line */
    .custom-hr {
        margin: 2.5rem 0;
        border: 0;
        height: 1px;
        background: linear-gradient(to right, rgba(0,0,0,0), rgba(226,232,240,1), rgba(0,0,0,0));
    }
    </style>
""", unsafe_allow_html=True)

# Aesthetic Header Area
st.markdown('<h1 class="hero-title">✨ DataExtract AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Convert any document into structured spreadsheets instantly.</p>', unsafe_allow_html=True)

# Elegant Document Uploader
uploaded_file = st.file_uploader("", type=["pdf", "csv", "xlsx", "txt"])

if uploaded_file:
    if "current_file" not in st.session_state or st.session_state.current_file != uploaded_file.name:
        with st.spinner("Analyzing document mapping..."):
            try:
                text = extract_text_from_file(uploaded_file)
                st.session_state.file_text = text
                st.session_state.detected_cols = detect_columns_with_ai(text)
                st.session_state.current_file = uploaded_file.name
            except Exception as e:
                st.error(f"Error analyzing document: {e}")
                st.session_state.detected_cols = []

    if st.session_state.detected_cols:
        st.markdown('<div class="custom-hr"></div>', unsafe_allow_html=True)
        
        # Dropdown selection
        selected_columns = st.multiselect(
            "Choose fields to extract:",
            options=st.session_state.detected_cols,
            default=st.session_state.detected_cols
        )
        
        if selected_columns:
            if st.button("Generate Clean Sheet"):
                with st.spinner("Structuring your data..."):
                    try:
                        raw_data = extract_details_with_ai(st.session_state.file_text, selected_columns)
                        
                        if "data" in raw_data:
                            data = raw_data["data"]
                        else:
                            key = list(raw_data.keys())[0] if raw_data.keys() else None
                            data = raw_data[key] if key and isinstance(raw_data[key], list) else [raw_data]

                        df = pd.DataFrame(data)
                        df.index = df.index + 1  # 1-based indexing for neat look
                        
                        st.markdown('<div class="custom-hr"></div>', unsafe_allow_html=True)
                        st.subheader("📊 Extracted Dataset")
                        st.dataframe(df, use_container_width=True)
                        
                        # Generate buffer
                        buffer = io.BytesIO()
                        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                            df.to_excel(writer, index=False)
                        
                        st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
                        st.download_button(
                            label="📥 Export to Excel",
                            data=buffer.getvalue(),
                            file_name="extracted_data.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    except Exception as e:
                        st.error(f"Extraction Error: {e}")
        else:
            st.warning("Please select at least one field heading.")
    else:
        st.warning("Could not automatically read any columns from this format.")
