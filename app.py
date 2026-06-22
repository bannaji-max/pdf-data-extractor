import streamlit as st
import pandas as pd
import io
from extractor import extract_text_from_file, detect_columns_with_ai, extract_details_with_ai

st.set_page_config(page_title="AI Multi-Data Extractor", page_icon="📄")
st.title("📄 Smart Document Data Extractor")

uploaded_file = st.file_uploader("Upload Document (PDF, CSV, XLSX, TXT)", type=["pdf", "csv", "xlsx", "txt"])

# Session state use kar rahe hain taaki file upload hone par columns ek hi baar detect hon
if uploaded_file:
    if "current_file" not in st.session_state or st.session_state.current_file != uploaded_file.name:
        with st.spinner("Analyzing document structure and detecting columns..."):
            try:
                text = extract_text_from_file(uploaded_file)
                st.session_state.file_text = text
                # AI se automatic columns detect karwana
                st.session_state.detected_cols = detect_columns_with_ai(text)
                st.session_state.current_file = uploaded_file.name
            except Exception as e:
                st.error(f"Error reading file: {e}")
                st.session_state.detected_cols = []

    if st.session_state.detected_cols:
        # Purane text input ki jagah ab Dropdown (Multi-select) aayega
        selected_columns = st.multiselect(
            "Select columns to extract from the document:",
            options=st.session_state.detected_cols,
            default=st.session_state.detected_cols # By default saare columns selected rahenge
        )
        
        if selected_columns:
            if st.button("Extract Data"):
                with st.spinner("Extracting data for selected columns..."):
                    try:
                        raw_data = extract_details_with_ai(st.session_state.file_text, selected_columns)
                        
                        if "data" in raw_data:
                            data = raw_data["data"]
                        else:
                            key = list(raw_data.keys())[0] if raw_data.keys() else None
                            data = raw_data[key] if key and isinstance(raw_data[key], list) else [raw_data]

                        df = pd.DataFrame(data)
                        df.index = df.index + 1
                        st.subheader("Results")
                        st.dataframe(df)
                        
                        buffer = io.BytesIO()
                        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                            df.to_excel(writer, index=False)
                        
                        st.download_button(
                            label="📥 Download Excel",
                            data=buffer.getvalue(),
                            file_name="extracted_data.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    except Exception as e:
                        st.error(f"Error extracting data: {e}")
        else:
            st.warning("Please select at least one column to extract.")
    else:
        st.warning("AI could not detect any columns. Try uploading a different or clearer document.")
