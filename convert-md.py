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
    # Debugging: Read the raw file content and display the first 500 characters
    raw_content = csv_file.getvalue().decode('utf-8', errors='ignore')[:500]
    st.write("Raw file content (first 500 characters):")
    st.write(raw_content)
    
    # Try to read the CSV file and display the first few rows
    try:
        df = pd.read_csv(csv_file)
        st.write("CSV Preview", df.head())  # Show a preview of the first few rows
    except Exception as e:
        st.error(f"Error reading CSV: {e}")
    
    # Try different delimiters if reading the CSV failed
    if df.empty:  # Check if DataFrame is empty
        try:
            st.write("Attempting to read with semicolon delimiter...")
            df = pd.read_csv(csv_file, delimiter=';')
            st.write("CSV Preview with semicolon delimiter", df.head())
        except Exception as e:
            st.error(f"Error reading CSV with semicolon delimiter: {e}")
        
    # Handle missing headers if the first row is not a header
    if df.empty:  # If still empty, try reading without headers
        try:
            st.write("Attempting to read without headers...")
            df = pd.read_csv(csv_file, header=None)
            df.columns = ['Name', 'Email', 'Phone', 'Address']  # Example, adjust to your columns
            st.write("CSV Preview without header", df.head())
        except Exception as e:
            st.error(f"Error reading CSV without header: {e}")

    # Try to read with a different encoding if the previous attempts failed
    if df.empty:
        try:
            st.write("Attempting to read with utf-8-sig encoding...")
            df = pd.read_csv(csv_file, encoding='utf-8-sig')
            st.write("CSV Preview with utf-8-sig encoding", df.head())
        except Exception as e:
            st.error(f"Error reading CSV with utf-8-sig encoding: {e}")

    # Button to trigger conversion to Markdown
    if not df.empty and st.button('Convert to Markdown'):
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
