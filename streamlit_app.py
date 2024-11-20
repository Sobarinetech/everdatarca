import streamlit as st
import google.generativeai as genai
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from langdetect import detect
from googletrans import Translator
import datetime
from io import BytesIO

# Configure the API key securely
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Streamlit App Configuration
st.set_page_config(page_title="Advanced Email Storytelling AI", page_icon="📧", layout="wide")
st.title("📧 Advanced Email Storytelling AI")
st.write("Transform your emails into insightful data stories, prioritize tasks, and generate AI-driven responses.")

# Sidebar for advanced features
st.sidebar.header("Customization & Features")
input_option = st.sidebar.radio("Select your input method:", ["Paste Email Content", "Upload Email File"])
summarization_style = st.sidebar.selectbox(
    "Choose summarization style:",
    ["Bullet Points", "Concise Paragraph", "Actionable Insights"]
)
enable_sentiment_analysis = st.sidebar.checkbox("Enable Sentiment Analysis")
enable_word_cloud = st.sidebar.checkbox("Generate Keyword Cloud")
enable_response_suggestion = st.sidebar.checkbox("Generate Suggested Response")
enable_multilingual_support = st.sidebar.checkbox("Enable Multilingual Processing")
theme = st.sidebar.radio("Select Theme:", ["Light Mode", "Dark Mode"])

# Dynamic Theme Application
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

# Processing Email Content
if email_content:
    st.subheader("Email Content Preview")
    st.text_area("Email Content:", email_content, height=150)

    # Multilingual Support
    if enable_multilingual_support:
        try:
            detected_lang = detect(email_content)
            if detected_lang != "en":
                st.info(f"Detected Language: {detected_lang.upper()} - Translating to English...")
                translator = Translator()
                email_content = translator.translate(email_content, src=detected_lang, dest="en").text
        except Exception as e:
            st.warning(f"Language detection/translation failed: {e}")

    if st.button("Generate Insights"):
        try:
            # Define the summarization prompt
            prompt = f"""
            Analyze the following email content and provide a summary in {summarization_style.lower()} style.
            Include key entities (names, dates, and terms), sentiment analysis, and generate actionable next steps:
            
            {email_content}
            """

            # Load and configure the model
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            
            # Display Summarization
            st.subheader("Generated Summary and Insights")
            st.write(response.text)

            # Sentiment Analysis
            if enable_sentiment_analysis:
                sentiment_prompt = f"Analyze the sentiment of this email (Positive, Negative, Neutral):\n\n{email_content}"
                sentiment_response = model.generate_content(sentiment_prompt)
                st.subheader("Sentiment Analysis")
                st.write(f"Email Sentiment: **{sentiment_response.text.strip()}**")

            # Generate Word Cloud
            if enable_word_cloud:
                wordcloud = WordCloud(width=800, height=400, background_color="white").generate(email_content)
                st.subheader("Keyword Cloud")
                fig, ax = plt.subplots()
                ax.imshow(wordcloud, interpolation="bilinear")
                ax.axis("off")
                st.pyplot(fig)

            # Response Suggestion
            if enable_response_suggestion:
                response_prompt = f"Generate a professional and concise response to the following email:\n\n{email_content}"
                response_suggestion = model.generate_content(response_prompt)
                st.subheader("Suggested Response")
                st.write(response_suggestion.text)

            # Save Summary Option
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
st.write("🌟 Advanced Features by Generative AI | Built with Streamlit")
