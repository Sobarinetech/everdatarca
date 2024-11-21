import streamlit as st
import google.generativeai as genai
from langdetect import detect
from googletrans import Translator
from io import BytesIO
from fpdf import FPDF
import concurrent.futures
import json
import time
from textblob import TextBlob

# Configure API Key securely from Streamlit's secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# App Configuration
st.set_page_config(page_title="Fast Email Storytelling AI", page_icon="", layout="wide")
st.title(" Lightning-Fast Email Storytelling AI")
st.write("Rapidly extract insights and generate professional responses from emails.")

# Sidebar for Features
st.sidebar.header("Settings")
features = {
    "sentiment": st.sidebar.checkbox("Perform Sentiment Analysis"),
    "highlights": st.sidebar.checkbox("Highlight Key Phrases"),
    "response": st.sidebar.checkbox("Generate Suggested Response"),
    "export": st.sidebar.checkbox("Export Options")
}

# Input Email Section
email_content = st.text_area("Paste your email content here:", height=200)

MAX_EMAIL_LENGTH = 1000

# Cache the AI responses to improve performance
@st.cache_data(ttl=3600)
def get_ai_response(prompt, email_content):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt + email_content[:MAX_EMAIL_LENGTH])
        return response.text.strip()
    except Exception as e:
        st.error(f"Error: {e}")
        return ""

def get_sentiment(email_content):
    return TextBlob(email_content).sentiment.polarity

def export_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    return pdf.output(dest='S').encode('latin1')

if email_content and st.button("Generate Insights"):
    try:
        detected_lang = detect(email_content)
        if detected_lang != "en":
            st.error("Only English language is supported.")
        else:
            with st.spinner("Generating insights..."):
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future_summary = executor.submit(get_ai_response, "Summarize the email in a concise, actionable format:\n\n", email_content)
                    future_response = executor.submit(get_ai_response, "Draft a professional response to this email:\n\n", email_content) if features["response"] else None
                    future_highlights = executor.submit(get_ai_response, "Highlight key points and actions in this email:\n\n", email_content) if features["highlights"] else None

                    summary = future_summary.result()
                    response = future_response.result() if future_response else ""
                    highlights = future_highlights.result() if future_highlights else ""

                st.subheader("AI Summary")
                st.write(summary)

                if features["response"]:
                    st.subheader("Suggested Response")
                    st.write(response)

                if features["highlights"]:
                    st.subheader("Key Highlights")
                    st.write(highlights)

                if features["sentiment"]:
                    sentiment = get_sentiment(email_content)
                    sentiment_label = "Positive" if sentiment > 0 else "Negative" if sentiment < 0 else "Neutral"
                    st.subheader("Sentiment Analysis")
                    st.write(f"**Sentiment:** {sentiment_label} (Polarity: {sentiment:.2f})")

                if features["export"]:
                    export_text = f"Summary:\n{summary}\n\nResponse:\n{response}\n\nHighlights:\n{highlights}"
                    export_json = {
                        "summary": summary,
                        "response": response,
                        "highlights": highlights,
                        "sentiment": sentiment_label if features["sentiment"] else None,
                    }

                    pdf_buffer = BytesIO(export_pdf(export_text))
                    buffer_txt = BytesIO(export_text.encode("utf-8"))
                    buffer_json = BytesIO(json.dumps(export_json, indent=4).encode("utf-8"))

                    st.download_button("Download as Text", data=buffer_txt, file_name="analysis.txt", mime="text/plain")
                    st.download_button("Download as JSON", data=buffer_json, file_name="analysis.json", mime="application/json")
                    st.download_button("Download as PDF", data=pdf_buffer, file_name="analysis.pdf", mime="application/pdf")

    except Exception as e:
        st.error(f"Error: {e}")

else:
    st.info("Paste email content and click 'Generate Insights' to start.")
