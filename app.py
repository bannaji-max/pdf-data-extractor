import streamlit as st
import pandas as pd
import io
from extractor import extract_text_from_pdf, extract_details_with_ai

st.set_page_config(page_title="AI Data Extractor", page_icon="📄")
st.title("📄 Smart Document Data Extractor")

uploaded_file = st.file_uploader("Upload PDF/Document", type=["pdf"])
columns_input = st.text_input("Enter columns (comma-separated)", placeholder="Name, Phone, Email")

if uploaded_file and columns_input:
    columns_list = [col.strip() for col in columns_input.split(",")]
    
    if st.button("Extract Data"):
        with st.spinner("Processing..."):
            try:
                text = extract_text_from_pdf(uploaded_file)
                raw_data = extract_details_with_ai(text, columns_list)
                
                if "data" in raw_data:
                    data = raw_data["data"]
                else:
                    key = list(raw_data.keys())[0] if raw_data.keys() else None
                    data = raw_data[key] if key and isinstance(raw_data[key], list) else [raw_data]

                df = pd.DataFrame(data)
                
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
                st.error(f"Error: {e}")
