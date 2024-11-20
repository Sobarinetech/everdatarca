import streamlit as st
import google.generativeai as genai
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from langdetect import detect
from googletrans import Translator
from io import BytesIO
import json
from fpdf import FPDF
from textblob import TextBlob

# Configure API Key
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# App Configuration
st.set_page_config(page_title="Precise Email Storytelling AI", page_icon="📧", layout="wide")
st.title("📧 Precise Email Storytelling AI")
st.write("Transform email content into precise, actionable insights with advanced AI analysis.")

# Sidebar for Advanced Features
st.sidebar.header("Features")
input_method = st.sidebar.radio("Input Method:", ["Paste Email Content", "Upload Email File"])
summarization_style = st.sidebar.selectbox(
    "Summarization Style:",
    ["Detailed Bullet Points", "Executive Summary", "Actionable Next Steps"]
)
enable_sentiment = st.sidebar.checkbox("Perform Sentiment Analysis")
enable_emotion_analysis = st.sidebar.checkbox("Perform Emotion Analysis")
enable_wordcloud = st.sidebar.checkbox("Generate Keyword Cloud")
enable_response = st.sidebar.checkbox("Generate Suggested Response")
multilingual_support = st.sidebar.checkbox("Enable Multilingual Support")
enable_highlights = st.sidebar.checkbox("Highlight Key Phrases and Entities")
enable_export = st.sidebar.checkbox("Enable Export Options (Text, PDF, JSON)")
theme = st.sidebar.radio("Theme:", ["Light", "Dark"])

# Apply Theme Dynamically
if theme == "Dark":
    st.markdown("""
        <style>
        body { background-color: #0E1117; color: #C8D0E0; }
        .stTextInput, .stButton, .stTextArea { background-color: #21262D; color: #C8D0E0; }
        </style>
        """, unsafe_allow_html=True)

# Input Email Section
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

            # Summarization with Specificity
            summarization_prompt = f"""
            Summarize this email content in {summarization_style.lower()} style. Include:
            - Key points
            - Actionable recommendations
            - Specific dates, names, and numbers if present.
            Content: {email_content}
            """
            model = genai.GenerativeModel("gemini-1.5-flash")
            summary_response = model.generate_content(summarization_prompt)

            st.subheader("Generated Summary")
            summary = summary_response.text.strip()
            st.write(summary)

            # Sentiment Analysis
            sentiment = ""
            if enable_sentiment:
                analysis = TextBlob(email_content)
                sentiment_score = analysis.sentiment.polarity
                sentiment = "Positive" if sentiment_score > 0 else "Negative" if sentiment_score < 0 else "Neutral"
                st.subheader("Sentiment Analysis")
                st.write(f"**Sentiment:** {sentiment} (Polarity: {sentiment_score:.2f})")

            # Emotion Analysis (Custom Rule-based Approach)
            if enable_emotion_analysis:
                emotion_prompt = f"Analyze the emotions in this email (e.g., Happy, Concerned, Frustrated):\n\n{email_content}"
                emotion_response = model.generate_content(emotion_prompt)
                emotions = emotion_response.text.strip()
                st.subheader("Emotion Analysis")
                st.write(f"**Emotions Identified:** {emotions}")

            # Word Cloud for Keywords
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
                suggested_response = response_suggestion.text.strip()
                st.subheader("Suggested Response")
                st.write(suggested_response)

            # Highlight Key Entities and Phrases
            if enable_highlights:
                highlight_prompt = f"Highlight key phrases, names, dates, and actions in this email:\n\n{email_content}"
                highlight_response = model.generate_content(highlight_prompt)
                highlights = highlight_response.text.strip()
                st.subheader("Key Highlights")
                st.write(highlights)

            # Export Options
            if enable_export:
                st.subheader("Export Options")
                buffer_txt = BytesIO()
                export_text = f"Summary:\n{summary}\n\nSentiment: {sentiment}\n\nEmotions: {emotions if enable_emotion_analysis else 'N/A'}\n\nSuggested Response:\n{suggested_response}"
                buffer_txt.write(export_text.encode("utf-8"))
                buffer_txt.seek(0)
                st.download_button("Download as Text", data=buffer_txt, file_name="email_analysis.txt", mime="text/plain")

                buffer_json = BytesIO()
                export_json = {
                    "summary": summary,
                    "sentiment": sentiment,
                    "emotions": emotions if enable_emotion_analysis else "N/A",
                    "suggested_response": suggested_response,
                    "highlights": highlights if enable_highlights else "N/A"
                }
                buffer_json.write(json.dumps(export_json, indent=4).encode("utf-8"))
                buffer_json.seek(0)
                st.download_button("Download as JSON", data=buffer_json, file_name="email_analysis.json", mime="application/json")

                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.multi_cell(0, 10, export_text)
                buffer_pdf = BytesIO()
                pdf.output(buffer_pdf)
                buffer_pdf.seek(0)
                st.download_button("Download as PDF", data=buffer_pdf, file_name="email_analysis.pdf", mime="application/pdf")

        except Exception as e:
            st.error(f"Error generating insights: {e}")
else:
    st.info("Please provide email content or upload a file to proceed.")

# Footer
st.markdown("---")
st.write("🌟 Built with precision by Generative AI | Powered by Streamlit")
