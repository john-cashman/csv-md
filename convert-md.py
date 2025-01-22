import streamlit as st
import pandas as pd
import html2text

# Initialize html2text converter
html_to_md = html2text.HTML2Text()
html_to_md.ignore_links = False  # Set to True if you want to ignore links

def convert_html_to_markdown(html_content):
    """
    Converts HTML content to Markdown using html2text.
    """
    return html_to_md.handle(html_content)

# Streamlit app
def main():
    st.title("HTML to Markdown Converter")

    # File uploader
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file is not None:
        # Read CSV
        try:
            df = pd.read_csv(uploaded_file)
            st.write("CSV File Preview:")
            st.dataframe(df)

            # Check for required columns
            if "article_title" in df.columns and "article_body" in df.columns:
                st.success("Found required columns: 'article_title' and 'article_body'")

                # Convert HTML to Markdown
                df["markdown_body"] = df["article_body"].apply(convert_html_to_markdown)

                # Display results
                st.subheader("Converted Markdown:")
                for _, row in df.iterrows():
                    st.markdown(f"### {row['article_title']}")
                    st.markdown(row["markdown_body"])
                    st.markdown("---")

                # Allow download of individual Markdown files as a ZIP
                if st.button("Download Markdown Files as ZIP"):
                    # Create ZIP of Markdown files
                    from io import BytesIO
                    import zipfile
                    import os

                    # Temporary directory for markdown files
                    temp_zip = BytesIO()
                    with zipfile.ZipFile(temp_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
                        for index, row in df.iterrows():
                            title = row["article_title"]
                            markdown_body = row["markdown_body"]
                            safe_title = "".join(c for c in title if c.isalnum() or c in " -_").rstrip()
                            filename = f"{safe_title or 'article'}_{index + 1}.md"
                            zipf.writestr(filename, f"# {title}\n\n{markdown_body}")
                    
                    temp_zip.seek(0)
                    st.download_button(
                        label="Download Markdown ZIP",
                        data=temp_zip,
                        file_name="markdown_files.zip",
                        mime="application/zip"
                    )
            else:
                st.error(
                    "The uploaded CSV file must contain 'article_title' and 'article_body' columns."
                )
        except Exception as e:
            st.error(f"Error processing file: {e}")

if __name__ == "__main__":
    main()
