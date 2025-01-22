import streamlit as st
import pandas as pd
import os
import zipfile
from bs4 import BeautifulSoup
from io import BytesIO
import shutil


# Function to convert HTML to Markdown
def convert_html_to_markdown(html_content, image_folder_name):
    """
    Converts HTML content to Markdown, referencing images from the specified folder.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Convert headings
    for level in range(1, 7):
        for tag in soup.find_all(f"h{level}"):
            tag.insert_before("#" * level + " ")
            tag.unwrap()
    
    # Convert paragraphs
    for tag in soup.find_all("p"):
        tag.insert_after("\n\n")
        tag.unwrap()
    
    # Convert images
    for img in soup.find_all("img"):
        src = img.get("src")
        if src:
            # Assume images are placed in the output folder's image subdirectory
            image_name = os.path.basename(src)
            img_markdown = f"![Image](./{image_folder_name}/{image_name})\n"
            img.insert_before(img_markdown)
        img.decompose()
    
    # Convert links
    for a in soup.find_all("a"):
        href = a.get("href")
        if href:
            a.insert_before(f"[{a.text}]({href})")
        a.unwrap()
    
    # Return the plain text with Markdown formatting
    return soup.get_text()


# Function to process a folder with HTML files and images
def process_html_folder(input_folder, output_folder_name):
    """
    Process a folder of HTML files and images, converting HTML to Markdown.
    """
    # Create output folders
    output_folder = os.path.join(input_folder, output_folder_name)
    os.makedirs(output_folder, exist_ok=True)

    image_folder = os.path.join(output_folder, "images")
    os.makedirs(image_folder, exist_ok=True)

    # Iterate through the files in the input folder
    for file_name in os.listdir(input_folder):
        input_path = os.path.join(input_folder, file_name)

        if file_name.endswith(".html"):
            # Read and convert the HTML file
            with open(input_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            
            markdown_content = convert_html_to_markdown(html_content, "images")

            # Save the Markdown file
            markdown_file_name = f"{os.path.splitext(file_name)[0]}.md"
            markdown_path = os.path.join(output_folder, markdown_file_name)
            with open(markdown_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)

        elif file_name.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".svg")):
            # Copy image files to the output image folder
            shutil.copy(input_path, image_folder)

    return output_folder


# Function to create a ZIP from a folder
def zip_output_folder(output_folder):
    """
    Compress the output folder into a ZIP file.
    """
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(output_folder):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(output_folder))
                zipf.write(file_path, arcname)
    
    zip_buffer.seek(0)
    return zip_buffer


# Streamlit App
def main():
    st.title("File to Markdown Converter with Images")

    # Allow user to select mode
    mode = st.radio("Choose input type:", ["CSV File", "HTML Folder"])

    if mode == "CSV File":
        # CSV File processing
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
                    st.error("The uploaded CSV file must contain 'article_title' and 'article_body' columns.")
            except Exception as e:
                st.error(f"Error processing file: {e}")

    elif mode == "HTML Folder":
        # Folder uploader
        uploaded_folder = st.file_uploader(
            "Upload a ZIP file containing HTML files and images", type=["zip"]
        )

        if uploaded_folder is not None:
            with zipfile.ZipFile(uploaded_folder, "r") as zip_ref:
                # Extract uploaded ZIP to a temporary directory
                temp_input_folder = "./temp_input"
                os.makedirs(temp_input_folder, exist_ok=True)
                zip_ref.extractall(temp_input_folder)

            st.success("Folder extracted successfully!")

            # Process the folder
            output_folder_name = "converted_markdown"
            output_folder = process_html_folder(temp_input_folder, output_folder_name)

            # Compress the output folder into a ZIP
            zip_buffer = zip_output_folder(output_folder)

            # Provide download link for the ZIP file
            st.download_button(
                label="Download Converted Markdown Files with Images",
                data=zip_buffer,
                file_name="converted_markdown.zip",
                mime="application/zip",
            )

            # Clean up temporary directories
            shutil.rmtree(temp_input_folder)
            shutil.rmtree(output_folder)


if __name__ == "__main__":
    main()
