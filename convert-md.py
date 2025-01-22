import streamlit as st
import pandas as pd
import os
import zipfile
from io import BytesIO

# Function to convert article title and body to Markdown
def convert_to_markdown(title, body):
    return f"# {title}\n\n{body}"

# Function to save Markdown files and create a ZIP folder
def create_markdown_zip(df):
    temp_dir = "temp_markdown_files"
    os.makedirs(temp_dir, exist_ok=True)

    for index, row in df.iterrows():
        title = row["article_title"]
        body = row["article_body"]
        markdown_content = convert_to_markdown(title, body)
        safe_title = "".join(c for c in title if c.isalnum() or c in " -_").rstrip()
        filename = f"{safe_title or 'article'}_{index + 1}.md"
        with open(os.path.join(temp_dir, filename), "w", encoding="utf-8") as f:
            f.write(markdown_content)

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_name in os.listdir(temp_dir):
            zipf.write(os.path.join(temp_dir, file_name), file_name)

    for file_name in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, file_name))
    os.rmdir(temp_dir)
    zip_buffer.seek(0)
    return zip_buffer

# Streamlit app
def main():
    st.title("CSV to Markdown File Generator")
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.write("CSV File Preview:")
            st.dataframe(df)

            if "article_title" in df.columns and "article_body" in df.columns:
                st.success("Found required columns: 'article_title' and 'article_body'")
                zip_buffer = create_markdown_zip(df)
                st.download_button(
                    label="Download Markdown Files as ZIP",
                    data=zip_buffer,
                    file_name="markdown_files.zip",
                    mime="application/zip",
                )
            else:
                st.error("The uploaded CSV must have 'article_title' and 'article_body' columns.")
        except Exception as e:
            st.error(f"Error processing file: {e}")

if __name__ == "__main__":
    main()
