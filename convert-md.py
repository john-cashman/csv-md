import streamlit as st
import os
import markdownify
from bs4 import BeautifulSoup
from io import BytesIO
import shutil
import zipfile


def convert_html_to_markdown(html_content, image_folder, output_folder):
    """
    Convert HTML to Markdown and adjust image paths.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # Update image references in HTML
    for img in soup.find_all("img"):
        src = img.get("src")
        if src:
            # Get the image name
            image_name = os.path.basename(src)

            # Update image reference in the output Markdown
            img["src"] = f"./{image_folder}/{image_name}"

    # Convert the updated HTML to Markdown
    return markdownify.markdownify(str(soup), heading_style="ATX")


def process_folder(input_folder, output_folder_name):
    """
    Process a folder of HTML files and images.
    """
    # Create an output folder
    output_folder = os.path.join(input_folder, output_folder_name)
    os.makedirs(output_folder, exist_ok=True)

    # Create an image subfolder in the output folder
    image_folder = os.path.join(output_folder, "images")
    os.makedirs(image_folder, exist_ok=True)

    # Iterate through files in the input folder
    for file_name in os.listdir(input_folder):
        input_path = os.path.join(input_folder, file_name)

        if file_name.endswith(".html"):
            # Read and convert HTML file
            with open(input_path, "r", encoding="utf-8") as f:
                html_content = f.read()

            markdown_content = convert_html_to_markdown(
                html_content, "images", output_folder
            )

            # Save the Markdown file
            markdown_file_name = f"{os.path.splitext(file_name)[0]}.md"
            markdown_path = os.path.join(output_folder, markdown_file_name)
            with open(markdown_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)

        elif file_name.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".svg")):
            # Copy image files to the images folder
            shutil.copy(input_path, image_folder)

    return output_folder


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
    st.title("HTML to Markdown Converter with Images")

    # Folder uploader (zip file containing folder structure)
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
        output_folder = process_folder(temp_input_folder, output_folder_name)

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
