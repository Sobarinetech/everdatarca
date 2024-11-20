import streamlit as st
import google.generativeai as genai
from io import BytesIO

# Configure the API key securely
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Streamlit App UI
st.set_page_config(page_title="Email Storytelling AI", page_icon="📧", layout="wide")
st.title("📧 Email Storytelling AI")
st.write("Transform your emails into actionable insights and summaries with the power of AI.")

# Sidebar for customization options
st.sidebar.header("Customization Options")
input_option = st.sidebar.radio("Select your input method:", ["Paste Email Content", "Upload Email File"])
summarization_style = st.sidebar.selectbox(
    "Choose summarization style:",
    ["Bullet Points", "Concise Paragraph", "Actionable Insights"]
)
theme = st.sidebar.radio("Select Theme:", ["Light Mode", "Dark Mode"])

# Adjust theme dynamically
if theme == "Dark Mode":
    st.markdown("""
        <style>
        body { background-color: #1E1E1E; color: #FFFFFF; }
        </style>
        """, unsafe_allow_html=True)

# Email Content Input
email_content = ""
if input_option == "Paste Email Content":
    email_content = st.text_area("Paste your email content here:", height=200)
elif input_option == "Upload Email File":
    uploaded_file = st.file_uploader("Upload an email text file:", type=["txt"])
    if uploaded_file is not None:
        email_content = uploaded_file.read().decode("utf-8")

# Summarization Process
if email_content:
    st.subheader("Email Content Preview")
    st.text_area("Email Content:", email_content, height=150)

    if st.button("Generate Insights"):
        try:
            # Define the summarization prompt
            prompt = f"""
            Analyze the following email content and provide a summary in {summarization_style.lower()} style.
            Include key entities (names, dates, and terms) and generate actionable next steps:
            
            {email_content}
            """

            # Load and configure the model
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            # Generate response
            response = model.generate_content(prompt)
            
            # Display results
            st.subheader("Generated Summary and Insights")
            st.write(response.text)

            # Key Entities Extraction
            key_entities_prompt = f"Extract key entities (names, dates, important terms) from the following text:\n\n{email_content}"
            key_entities_response = model.generate_content(key_entities_prompt)
            st.subheader("Key Entities")
            st.write(key_entities_response.text)

            # Save results option
            buffer = BytesIO()
            buffer.write(response.text.encode('utf-8'))
            buffer.seek(0)
            st.download_button(
                label="Download Summary",
                data=buffer,
                file_name="email_summary.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"Error: {e}")
else:
    st.warning("Please provide email content or upload a file to proceed.")

# Footer
st.markdown("---")
st.write("🔗 Powered by Generative AI | Built with Streamlit")
