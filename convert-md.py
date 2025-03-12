import streamlit as st
import pandas as pd
import os
import zipfile
from io import BytesIO
import re
from bs4 import BeautifulSoup

# Function to convert article title and body to Markdown
def convert_to_markdown(title, body):
    # Parse the body for HTML callouts and convert them
    body = convert_callouts_to_markdown(body)
    return f"# {title}\n\n{body}"

# Function to convert HTML callouts to Markdown {% hint style="info" %}
def convert_callouts_to_markdown(html_body):
    soup = BeautifulSoup(html_body, "html.parser")
    
    # Find all divs with the class 'callout callout--transparent'
    callouts = soup.find_all("div", class_="callout callout--transparent")
    
    for callout in callouts:
        h4_tag = callout.find("h4", class_="callout__title")
        p_tag = callout.find("p")
        
        if h4_tag and p_tag:
            title = h4_tag.get_text(strip=True)
            content = p_tag.get_text(strip=True)
            
            # Ensure links are in Markdown format and add spacing between paragraphs and links
            content = convert_links_to_markdown(content)
            
            # Convert to the {% hint style="info" %} format
            hint_markdown = f"\n{{% hint style=\"info\" %}}\n**{title}**\n\n{content}\n{{% endhint %}}\n"
            
            # Replace the callout HTML with the Markdown version
            callout.insert_before(hint_markdown)
            callout.decompose()  # Remove the original HTML callout
    
    # Return the modified HTML as Markdown
    return str(soup)

# Function to convert links in the text to Markdown format and ensure space between paragraphs and links
def convert_links_to_markdown(text):
    # Parse the text as HTML
    soup = BeautifulSoup(text, "html.parser")
    
    for a_tag in soup.find_all("a"):
        link_text = a_tag.get_text()
        link_url = a_tag.get("href")
        
        # Create Markdown link
        markdown_link = f"[{link_text}]({link_url})"
        
        # Replace the <a> tag with the Markdown link
        a_tag.replace_with(markdown_link)

    # Convert the updated HTML back to text
    markdown_text = soup.get_text()

    # Ensure a space is added after each link if not present
    markdown_text = re.sub(r'(\]\([^)]+\))(?=\S)', r'\1 ', markdown_text)

    return markdown_text

# Function to save markdown files into section folders, create a summary file, and a zip folder
def create_markdown_zip(df):
    # Temporary directory to store markdown files
    temp_dir = "temp_markdown_files"
    os.makedirs(temp_dir, exist_ok=True)

    # Ensure the required columns exist
    if not all(col in df.columns for col in ["Article Body", "Section", "Article Title"]):
        st.error("The CSV file must contain `Article Body`, `Section`, and `Article Title` columns.")
        return None

    # Dictionary to store structure for the SUMMARY.md file
    summary_structure = {}

    # Iterate over rows to create files
    for index, row in df.iterrows():
        title = row["Article Title"]
        body = row["Article Body"]
        section = row["Section"]

        # Remove numbers from the title
        title = re.sub(r'\d+', '', title)  # Remove all digits from the title

        markdown_content = convert_to_markdown(title, body)

        # Safe file name creation: Remove digits and replace spaces with hyphens
        safe_title = "".join(c for c in title if c.isalnum() or c in " -_").rstrip()
        safe_title = safe_title.replace(" ", "-").lower()  # Replace spaces with hyphens and lowercase
        filename = f"{safe_title or 'article'}.md"  # Filename without numbers

        # Create section subfolder (with hyphens in section names)
        safe_section = section.replace(" ", "-").lower() 
        section_folder = os.path.join(temp_dir, safe_section)
        os.makedirs(section_folder, exist_ok=True)

        # Save the markdown file in the appropriate section folder
        file_path = os.path.join(section_folder, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        # Update the summary structure
        if section not in summary_structure:
            summary_structure[section] = []
        summary_structure[section].append((title, f"{safe_section}/{filename}"))

    # Create the SUMMARY.md file
    summary_content = "# Table of contents\n\n"
    for section, pages in summary_structure.items():
        summary_content += f"## {section}\n"
        for page_title, page_path in pages:
            summary_content += f"* [{page_title}]({page_path})\n"
        summary_content += "\n"

    # Save SUMMARY.md in the root of temp_dir
    with open(os.path.join(temp_dir, "SUMMARY.md"), "w", encoding="utf-8") as summary_file:
        summary_file.write(summary_content)

    # Create a ZIP file containing all section folders, markdown files, and the SUMMARY.md file
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file_name in files:
                full_path = os.path.join(root, file_name)
                arcname = os.path.relpath(full_path, temp_dir)  # Preserve folder structure
                zipf.write(full_path, arcname)

    # Clean up temporary directory
    for root, dirs, files in os.walk(temp_dir, topdown=False):
        for file_name in files:
            os.remove(os.path.join(root, file_name))
        for dir_name in dirs:
            os.rmdir(os.path.join(root, dir_name))
    os.rmdir(temp_dir)
    
    zip_buffer.seek(0)
    return zip_buffer

# Streamlit app
def main():
    st.title("Zendesk CSV to Markdown")

    # Displaying instructions
    st.info("""
    Upload a CSV file that contains three columns: `Article Body`, `Section`, and `Article Title`. 
    The file should look like this:

    | Article Title       | Article Body        | Section    |
    |---------------------|---------------------|------------|
    | Sample Title 1      | This is the content | Section-1  |
    | Sample Title 2      | Another body text   | Section-2  |
    """)

    # File uploader
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file is not None:
        # Read the CSV file
        try:
            df = pd.read_csv(uploaded_file)
            st.write("CSV File Preview:")
            st.dataframe(df)

            # Check for required columns
            required_columns = ["Article Body", "Section", "Article Title"]
            if all(col in df.columns for col in required_columns):
                st.success("Found required columns!")
                
                # Button to generate Markdown files with sections
                if st.button("Generate Markdown Files"):
                    zip_buffer = create_markdown_zip(df)
                    
                    if zip_buffer:
                        # Provide download link for ZIP file
                        st.success("Markdown files generated successfully!")
                        st.download_button(
                            label="Download ZIP file",
                            data=zip_buffer,
                            file_name="markdown_files_with_summary.zip",
                            mime="application/zip",
                        )
            else:
                st.error("The CSV file must contain `Article Body`, `Section`, and `Article Title` columns.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
