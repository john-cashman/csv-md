import streamlit as st
import pandas as pd
import os

# Function to convert CSV to Markdown files
def convert_csv_to_md(csv_file):
    try:
        # Directly read the CSV from the uploaded file-like object
        df = pd.read_csv(csv_file)
    except pd.errors.EmptyDataError:
        st.error("The CSV file is empty or has an invalid format.")
        return []
    except Exception as e:
        st.error(f"An error occurred while reading the CSV file: {e}")
        return []
    
    # Create a folder to store the converted Markdown files
    output_folder = 'converted_md_files'
    os.makedirs(output_folder, exist_ok=True)

    # List to hold the file paths of the generated Markdown files
    md_files = []

    # Convert each row in the DataFrame to a Markdown file
    for index, row in df.iterrows():
        contact_name = row.get('Name', f'Contact_{index}')  # Default to 'Contact_{index}' if 'Name' column is missing
        md_content = f"# {contact_name}\n\n"

        # Loop through each column in the row and add it to the Markdown content
        for column, value in row.items():
            md_content += f"**{column}:** {value}\n\n"

        # Define the file name and file path for the Markdown file
        file_name = f"{contact_name.replace(' ', '_')}.md"
        file_path = os.path.join(output_folder, file_name)

        # Save the Markdown content to the file
        with open(file_path, 'w', encoding='utf-8') as md_file:
            md_file.write(md_content)

        md_files.append(file_path)

    return md_files

# Streamlit UI
st.title("CSV to Markdown Converter")

st.markdown("""
Upload a CSV file, and the app will convert each row (contact) into a separate Markdown file.
""")

# File uploader widget
csv_file = st.file_uploader("Choose a CSV file", type="csv")

if csv_file:
    # Debugging: Show the file type and size
    st.write(f"File type: {csv_file.type}")
    st.write(f"File size: {csv_file.size} bytes")

    # Debugging: Display the raw file content (first 500 characters)
    file_content = csv_file.getvalue().decode('utf-8', errors='ignore')[:500]
    st.write("Raw file content preview (first 500 characters):")
    st.write(file_content)

    # Read the uploaded CSV file (use the file-like object directly)
    try:
        df = pd.read_csv(csv_file)
        st.write("CSV Preview", df.head())  # Show the first few rows of the CSV for preview
    except pd.errors.EmptyDataError:
        st.error("The CSV file is empty or cannot be read.")
    except Exception as e:
        st.error(f"An error occurred while reading the file: {e}")

    # Button to trigger conversion to Markdown
    if st.button('Convert to Markdown'):
        # Convert the uploaded CSV file into Markdown files
        md_files = convert_csv_to_md(csv_file)

        # Inform the user that the conversion is complete
        if md_files:
            st.write("Conversion complete! You can now download the individual Markdown files:")

            # Provide download links for each generated Markdown file
            for md_file in md_files:
                with open(md_file, 'r', encoding='utf-8') as file:
                    md_content = file.read()

                st.download_button(
                    label=f"Download {os.path.basename(md_file)}",
                    data=md_content,
                    file_name=os.path.basename(md_file),
                    mime="text/markdown"
                )
