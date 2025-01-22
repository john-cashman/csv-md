
    import pandas as pd
    import streamlit as st
    from bs4 import BeautifulSoup
    st.write("Dependencies loaded successfully!")
except Exception as e:
    st.error(f"Error loading dependencies: {e}")

# Function to convert article title and body to Markdown
def convert_to_markdown(title, body):
    return f"# {title}\n\n{body}"

# Function to save Markdown files and create a ZIP folder from a CSV
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

# Function to convert HTML to Markdown
def convert_html_to_markdown(html_content, image_folder_name):
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
    
    return soup.get_text()

# Function to process a folder with HTML files and images
def process_html_folder(input_folder, output_folder_name):
    output_folder = os.path.join(input_folder, output_folder_name)
    os.makedirs(output_folder, exist_ok=True)

    image_folder = os.path.join(output_folder, "images")
    os.makedirs(image_folder, exist_ok=True)

    for file_name in os.listdir(input_folder):
        input_path = os.path.join(input_folder, file_name)

        if file_name.endswith(".html"):
            with open(input_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            markdown_content = convert_html_to_markdown(html_content, "images")
            markdown_file_name = f"{os.path.splitext(file_name)[0]}.md"
            markdown_path = os.path.join(output_folder, markdown_file_name)
            with open(markdown_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)

        elif file_name.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".svg")):
            shutil.copy(input_path, image_folder)

    return output_folder

# Function to create a ZIP from a folder
def zip_output_folder(output_folder):
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

    mode = st.radio("Choose input type:", ["CSV File", "HTML Folder"])

    if mode == "CSV File":
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
                    st.error("The uploaded CSV file must contain 'article_title' and 'article_body' columns.")
            except Exception as e:
                st.error(f"Error processing file: {e}")

    elif mode == "HTML Folder":
        uploaded_folder = st.file_uploader(
            "Upload a ZIP file containing HTML files and images", type=["zip"]
        )
        if uploaded_folder is not None:
            with zipfile.ZipFile(uploaded_folder, "r") as zip_ref:
                temp_input_folder = "./temp_input"
                os.makedirs(temp_input_folder, exist_ok=True)
                zip_ref.extractall(temp_input_folder)

            st.success("Folder extracted successfully!")

            output_folder_name = "converted_markdown"
            output_folder = process_html_folder(temp_input_folder, output_folder_name)
            zip_buffer = zip_output_folder(output_folder)
            st.download_button(
                label="Download Converted Markdown Files with Images",
                data=zip_buffer,
                file_name="converted_markdown.zip",
                mime="application/zip",
            )
            shutil.rmtree(temp_input_folder)
            shutil.rmtree(output_folder)

if __name__ == "__main__":
    main()
