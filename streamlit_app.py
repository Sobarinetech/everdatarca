import streamlit as st
import google.generativeai as genai
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from langdetect import detect
from googletrans import Translator
from io import BytesIO

# Configure the API key securely
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Streamlit App Configuration
st.set_page_config(page_title="Email Storytelling AI", page_icon="📧", layout="wide")
st.title("📧 Email Storytelling AI")
st.write("Turn your email content into actionable insights, summaries, and visualizations.")

# Sidebar for feature selection
st.sidebar.header("Features")
input_method = st.sidebar.radio("Input Method:", ["Paste Email Content", "Upload Email File"])
summarization_style = st.sidebar.selectbox(
    "Summarization Style:", 
    ["Bullet Points", "Concise Paragraph", "Actionable Insights"]
)
enable_sentiment = st.sidebar.checkbox("Enable Sentiment Analysis")
enable_wordcloud = st.sidebar.checkbox("Generate Word Cloud")
enable_response = st.sidebar.checkbox("Generate Suggested Response")
multilingual_support = st.sidebar.checkbox("Enable Multilingual Support")
theme = st.sidebar.radio("Theme:", ["Light", "Dark"])

# Apply theme dynamically
if theme == "Dark":
    st.markdown("""
        <style>
        body { background-color: #0E1117; color: #C8D0E0; }
        .stTextInput, .stButton, .stTextArea { background-color: #21262D; color: #C8D0E0; }
        </style>
        """, unsafe_allow_html=True)

# Email Input Section
st.subheader("Input Email Content")
email_content = ""
if input_method == "Paste Email Content":
    email_content = st.text_area("Paste your email content here:", height=200)
elif input_method == "Upload Email File":
    uploaded_file = st.file_uploader("Upload an email text file:", type=["txt"])
    if uploaded_file:
        email_content = uploaded_file.read().decode("utf-8")

if email_content:
    st.subheader("Preview Email Content")
    st.write(email_content[:500] + "..." if len(email_content) > 500 else email_content)

    if st.button("Generate Insights"):
        try:
            # Multilingual Support
            if multilingual_support:
                detected_lang = detect(email_content)
                if detected_lang != "en":
                    st.info(f"Detected Language: {detected_lang.upper()} - Translating to English...")
                    translator = Translator()
                    email_content = translator.translate(email_content, src=detected_lang, dest="en").text

            # Summarization Prompt
            prompt = f"""
            Summarize this email content in {summarization_style.lower()} style. Include key entities, action items, and insights:
            {email_content}
            """
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)

            st.subheader("Generated Summary")
            st.write(response.text)

            # Sentiment Analysis
            if enable_sentiment:
                sentiment_prompt = f"Analyze the sentiment of this email (Positive, Negative, Neutral):\n\n{email_content}"
                sentiment_response = model.generate_content(sentiment_prompt)
                st.subheader("Sentiment Analysis")
                st.write(f"**Sentiment:** {sentiment_response.text.strip()}")

            # Word Cloud Generation
            if enable_wordcloud:
                wordcloud = WordCloud(width=800, height=400, background_color="white").generate(email_content)
                st.subheader("Keyword Cloud")
                fig, ax = plt.subplots()
                ax.imshow(wordcloud, interpolation="bilinear")
                ax.axis("off")
                st.pyplot(fig)

            # Suggested Response
            if enable_response:
                response_prompt = f"Generate a professional and concise response to this email:\n\n{email_content}"
                response_suggestion = model.generate_content(response_prompt)
                st.subheader("Suggested Response")
                st.write(response_suggestion.text)

            # Download Option
            buffer = BytesIO()
            buffer.write(response.text.encode("utf-8"))
            buffer.seek(0)
            st.download_button(
                label="Download Summary",
                data=buffer,
                file_name="email_summary.txt",
                mime="text/plain"
            )
        except Exception as e:
            st.error(f"Error generating insights: {e}")
else:
    st.info("Please provide email content or upload a file to proceed.")

# Footer
st.markdown("---")
st.write("🌟 Powered by Generative AI | Built with Streamlit")
