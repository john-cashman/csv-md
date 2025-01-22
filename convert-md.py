import streamlit as st
import pandas as pd
import os
import zipfile
from io import BytesIO

# Function to convert article title and body to Markdown
def convert_to_markdown(title, body):
    return f"# {title}\n\n{body}"

# Function to save markdown files and create a zip folder
def create_markdown_zip(df):
    # Temporary directory to store markdown files
    temp_dir = "temp_markdown_files"
    os.makedirs(temp_dir, exist_ok=True)

    # Create individual markdown files
    for index, row in df.iterrows():
        title = row["article_title"]
        body = row["article_body"]
        markdown_content = convert_to_markdown(title, body)
        
        # Safe file name creation
        safe_title = "".join(c for c in title if c.isalnum() or c in " -_").rstrip()
        filename = f"{safe_title or 'article'}_{index + 1}.md"
        
        with open(os.path.join(temp_dir, filename), "w", encoding="utf-8") as f:
            f.write(markdown_content)
    
    # Create a ZIP file containing all markdown files
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_name in os.listdir(temp_dir):
            zipf.write(os.path.join(temp_dir, file_name), file_name)
    
    # Clean up temporary directory
    for file_name in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, file_name))
    os.rmdir(temp_dir)
    
    zip_buffer.seek(0)
    return zip_buffer

# Streamlit app
def main():
    st.title("CSV to Markdown File Generator")

    # File uploader
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file is not None:
        # Read the CSV file
        try:
            df = pd.read_csv(uploaded_file)
            st.write("CSV File Preview:")
            st.dataframe(df)

            # Check for required columns
            if "article_title" in df.columns and "article_body" in df.columns:
                st.success("Found required columns: 'article_title' and 'article_body'")

                # Create ZIP of Markdown files
                zip_buffer = create_markdown_zip(df)

                # Provide download link for the ZIP file
                st.download_button(
                    label="Download Markdown Files as ZIP",
                    data=zip_buffer,
                    file_name="markdown_files.zip",
                    mime="application/zip",
                )
            else:
                st.error(
                    "The uploaded CSV file must contain 'article_title' and 'article_body' columns."
                )
        except Exception as e:
            st.error(f"Error processing file: {e}")

if __name__ == "__main__":
    main()
