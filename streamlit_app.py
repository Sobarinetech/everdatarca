import streamlit as st
import google.generativeai as genai
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from langdetect import detect
from googletrans import Translator
from io import BytesIO
from fpdf import FPDF
import threading
import json
from textblob import TextBlob

# Configure API Key securely from Streamlit's secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# App Configuration
st.set_page_config(page_title="Fast Email Storytelling AI", page_icon="⚡", layout="wide")
st.title("⚡ Lightning-Fast Email Storytelling AI")
st.write("Rapidly extract insights and generate professional responses from emails.")

# Sidebar for Features
st.sidebar.header("Settings")
enable_wordcloud = st.sidebar.checkbox("Generate Word Cloud")
enable_sentiment = st.sidebar.checkbox("Perform Sentiment Analysis")
enable_highlights = st.sidebar.checkbox("Highlight Key Phrases")
enable_response = st.sidebar.checkbox("Generate Suggested Response")
enable_export = st.sidebar.checkbox("Export Options (Text, JSON, PDF)")

# Input Email Section
st.subheader("Input Email Content")
email_content = st.text_area("Paste your email content here:", height=200)

def generate_export_files(export_text, export_json):
    # Generate PDF content and store in buffer
    pdf_content = export_pdf(export_text)
    pdf_buffer = BytesIO(pdf_content)

    # Provide download buttons
    return pdf_buffer, export_text, export_json

def export_pdf(export_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, export_text)
    return pdf.output(dest='S').encode('latin1')  # Return PDF content as bytes

if email_content and st.button("Generate Insights"):
    try:
        # Step 1: Detect and Translate Language (if necessary)
        detected_lang = "en"
        if st.sidebar.checkbox("Enable Multilingual Translation"):
            detected_lang = detect(email_content)
            if detected_lang != "en":
                st.info(f"Detected Language: {detected_lang.upper()} - Translating...")
                translator = Translator()
                email_content = translator.translate(email_content, src=detected_lang, dest="en").text

        # Step 2: Generate AI Insights
        with st.spinner("Generating insights..."):
            model = genai.GenerativeModel("gemini-1.5-flash")
            summary_prompt = f"Summarize the email in a concise, actionable format:\n\n{email_content}"
            summary_response = model.generate_content(summary_prompt)
            summary = summary_response.text.strip()

            response = ""
            if enable_response:
                response_prompt = f"Draft a professional response to this email:\n\n{email_content}"
                response_response = model.generate_content(response_prompt)
                response = response_response.text.strip()

            highlights = ""
            if enable_highlights:
                highlight_prompt = f"Highlight key points and actions in this email:\n\n{email_content}"
                highlight_response = model.generate_content(highlight_prompt)
                highlights = highlight_response.text.strip()

        # Step 3: Display Results
        st.subheader("AI Summary")
        st.write(summary)

        if enable_response:
            st.subheader("Suggested Response")
            st.write(response)

        if enable_highlights:
            st.subheader("Key Highlights")
            st.write(highlights)

        # Step 4: Sentiment Analysis (Quick)
        if enable_sentiment:
            sentiment = TextBlob(email_content).sentiment
            polarity = sentiment.polarity
            sentiment_label = "Positive" if polarity > 0 else "Negative" if polarity < 0 else "Neutral"
            st.subheader("Sentiment Analysis")
            st.write(f"**Sentiment:** {sentiment_label} (Polarity: {polarity:.2f})")

        # Step 5: Word Cloud (Optional)
        if enable_wordcloud:
            st.subheader("Word Cloud")
            wordcloud = WordCloud(width=800, height=400, background_color="white").generate(email_content)
            fig, ax = plt.subplots()
            ax.imshow(wordcloud, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)

        # Step 6: Export Options
        if enable_export:
            st.subheader("Export Results")
            export_text = f"Summary:\n{summary}\n\nResponse:\n{response}\n\nHighlights:\n{highlights}"
            export_json = {
                "summary": summary,
                "response": response,
                "highlights": highlights,
                "sentiment": sentiment_label if enable_sentiment else None,
            }

            # Generate exportable formats and handle in threads
            pdf_buffer, export_text, export_json = generate_export_files(export_text, export_json)

            # Provide download buttons
            buffer_txt = BytesIO(export_text.encode("utf-8"))
            buffer_json = BytesIO(json.dumps(export_json, indent=4).encode("utf-8"))
            st.download_button("Download as Text", data=buffer_txt, file_name="analysis.txt", mime="text/plain")
            st.download_button("Download as JSON", data=buffer_json, file_name="analysis.json", mime="application/json")
            st.download_button("Download as PDF", data=pdf_buffer, file_name="analysis.pdf", mime="application/pdf")

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Paste email content and click 'Generate Insights' to start.")

# Footer
st.markdown("---")
st.write("⚡ Built for Speed | Powered by Generative AI | Streamlit")
