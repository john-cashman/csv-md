import streamlit as st
import pandas as pd
import io

# Function to convert CSV to a single markdown file
def convert_csv_to_markdown(csv_file):
    try:
        # Read the CSV file using pandas
        df = pd.read_csv(csv_file)
    except Exception as e:
        st.error(f"Error reading CSV file: {e}")
        return None
    
    # Initialize markdown content
    markdown_content = ""
    
    # Loop over each row in the dataframe and convert it into a markdown page
    for index, row in df.iterrows():
        contact_name = row.get('Name', f'Contact_{index}')  # Use 'Name' column as title or fallback to 'Contact_{index}'
        
        # Add a markdown page for each row
        markdown_content += f"# {contact_name}\n\n"  # Use 'Name' for the page title (can be customized)
        
        # Add each column as a key-value pair in markdown format
        for column, value in row.items():
            markdown_content += f"**{column}:** {value}\n\n"
        
        # Add a page separator (---) to separate each contact's markdown page
        markdown_content += "\n---\n\n"
    
    return markdown_content

# Streamlit UI
st.title("CSV to Markdown Converter")

st.markdown("""
Upload a CSV file, and the app will convert each row (contact) into a separate Markdown page.
""")

# File uploader widget
csv_file = st.file_uploader("Choose a CSV file", type="csv")

if csv_file:
    # Show a preview of the CSV data
    try:
        # Read the uploaded CSV file and display a preview of the first few rows
        df = pd.read_csv(csv_file)
        st.write("CSV Preview", df.head())
    except Exception as e:
        st.error(f"Error reading CSV: {e}")

    # Button to trigger conversion to Markdown
    if st.button('Convert to Markdown'):
        # Convert the uploaded CSV file into Markdown content
        markdown_content = convert_csv_to_markdown(csv_file)

        if markdown_content:
            # Provide a download button for the generated Markdown file
            st.write("Conversion complete! Download your Markdown file below:")

            # Provide the download button
            st.download_button(
                label="Download Markdown File",
                data=markdown_content,
                file_name="contacts.md",
                mime="text/markdown"
            )
