import streamlit as st
import pandas as pd

# Function to convert article title and body to Markdown
def convert_to_markdown(title, body):
    return f"# {title}\n\n{body}"

# Streamlit app
def main():
    st.title("CSV to Markdown Converter")

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

                # Convert each row to Markdown
                markdown_texts = [
                    convert_to_markdown(row["article_title"], row["article_body"])
                    for _, row in df.iterrows()
                ]

                # Display Markdown
                st.subheader("Generated Markdown:")
                for md_text in markdown_texts:
                    st.markdown(md_text)
                    st.markdown("---")

                # Option to download all markdowns
                full_markdown = "\n\n---\n\n".join(markdown_texts)
                st.download_button(
                    label="Download All as Markdown",
                    data=full_markdown,
                    file_name="articles.md",
                    mime="text/markdown",
                )
            else:
                st.error(
                    "The uploaded CSV file must contain 'article_title' and 'article_body' columns."
                )
        except Exception as e:
            st.error(f"Error processing file: {e}")

if __name__ == "__main__":
    main()
