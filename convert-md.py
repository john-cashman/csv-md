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
    # Convert links from HTML <a> tags to Markdown
    soup = BeautifulSoup(text, "html.parser")
    
    for a_tag in soup.find_all("a"):
        link_text = a_tag.get_text()
        link_url = a_tag.get("href")
        
        # Create Markdown link
        markdown_link = f"[{link_text}]({link_url})"
        
        # Replace the <a> tag with the Markdown link
        a_tag.replace_with(markdown_link)

    # Ensure a newline between paragraph content and any link
    return str(soup).replace("\n", "\n\n")

# Function to save markdown files and create a zip folder
def create_markdown_zip(df):
    # Temporary directory to store markdown files
    temp_dir = "temp_markdown_files"
    os.makedirs(temp_dir, exist_ok=True)

    # Create individual markdown files
    for index, row in df.iterrows():
        title = row["article_title"]
        body = row["article_body"]
        
        # Remove numbers from the title
        title = re.sub(r'\d+', '', title)  # Remove all digits from the title
        
        markdown_content = convert_to_markdown(title, body)

        # Safe file name creation: Remove digits and replace spaces with hyphens
        safe_title = "".join(c for c in title if c.isalnum() or c in " -_").rstrip()
        safe_title = safe_title.replace(" ", "-")  # Replace spaces with hyphens
        filename = f"{safe_title or 'article'}.md"  # Filename without numbers
        
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
    st.title("CSV to Markdown File Generator 2")

    # Displaying instructions
    st.info("""
    Upload a CSV file that contains two columns: `article_title` and `article_body`. 
    The file should look like this:

    | article_title       | article_body        |
    |---------------------|---------------------|
    | Sample Title 1      | This is the content |
    | Sample Title 2      | Another body text   |
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
            if "article_title" in df.columns and "article_body" in df.columns:
                st.success("Found required col
