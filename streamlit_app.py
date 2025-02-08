import streamlit as st
import google.generativeai as genai
from langdetect import detect
from textblob import TextBlob
from fpdf import FPDF
from io import BytesIO
import concurrent.futures
import json
import time

# Configure API Key securely from Streamlit's secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Streamlit App Configuration
st.set_page_config(page_title="Fast Email Storytelling AI", page_icon="📧", layout="wide")
st.title("📨 Lightning-Fast Email Storytelling AI")
st.write("Extract insights, generate professional responses, and analyze emails in real-time.")

# Sidebar for Features
st.sidebar.header("Settings")
features = {
    "sentiment": st.sidebar.checkbox("Perform Sentiment Analysis"),
    "highlights": st.sidebar.checkbox("Highlight Key Phrases"),
    "response": st.sidebar.checkbox("Generate Suggested Response"),
    "export": st.sidebar.checkbox("Enable Export Options"),
    "tone": st.sidebar.checkbox("Detect Email Tone"),
    "urgency": st.sidebar.checkbox("Analyze Urgency"),
    "task_extraction": st.sidebar.checkbox("Extract Actionable Tasks"),
    "subject_recommendation": st.sidebar.checkbox("Recommend Subject Line"),
    "category": st.sidebar.checkbox("Categorize Email Type"),
    "politeness": st.sidebar.checkbox("Check Politeness Score"),
    "emotion": st.sidebar.checkbox("Analyze Emotion"),
    "spam_check": st.sidebar.checkbox("Detect Spam/Scam"),
    "readability": st.sidebar.checkbox("Check Readability Score"),
}

# Email Input Section
email_content = st.text_area("📩 Paste your email content here:", height=200)

MAX_EMAIL_LENGTH = 2000  # Increased for better analysis

# Cache AI Responses to Improve Performance
@st.cache_data(ttl=3600)
def get_ai_response(prompt, email_content):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt + email_content[:MAX_EMAIL_LENGTH])
        return response.text.strip()
    except Exception as e:
        st.error(f"AI Error: {e}")
        return ""

# Additional Analysis Functions
def get_sentiment(email_content):
    return TextBlob(email_content).sentiment.polarity

def get_readability(email_content):
    return round(TextBlob(email_content).sentiment.subjectivity * 10, 2)  # Rough readability proxy

def export_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    return pdf.output(dest='S').encode('latin1')

# Processing Email When Button Clicked
if email_content and st.button("🔍 Generate Insights"):
    try:
        detected_lang = detect(email_content)
        if detected_lang != "en":
            st.error("⚠️ Only English language is supported.")
        else:
            with st.spinner("⚡ Processing email insights..."):
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future_summary = executor.submit(get_ai_response, "Summarize this email concisely:\n\n", email_content)
                    future_response = executor.submit(get_ai_response, "Draft a professional response:\n\n", email_content) if features["response"] else None
                    future_highlights = executor.submit(get_ai_response, "Highlight key points:\n\n", email_content) if features["highlights"] else None
                    future_tone = executor.submit(get_ai_response, "Detect the tone of this email:\n\n", email_content) if features["tone"] else None
                    future_urgency = executor.submit(get_ai_response, "Analyze urgency level:\n\n", email_content) if features["urgency"] else None
                    future_tasks = executor.submit(get_ai_response, "List actionable tasks:\n\n", email_content) if features["task_extraction"] else None
                    future_subject = executor.submit(get_ai_response, "Suggest a professional subject line:\n\n", email_content) if features["subject_recommendation"] else None
                    future_category = executor.submit(get_ai_response, "Categorize this email:\n\n", email_content) if features["category"] else None
                    future_politeness = executor.submit(get_ai_response, "Evaluate politeness score:\n\n", email_content) if features["politeness"] else None
                    future_emotion = executor.submit(get_ai_response, "Analyze emotions in this email:\n\n", email_content) if features["emotion"] else None
                    future_spam = executor.submit(get_ai_response, "Detect if this email is spam/scam:\n\n", email_content) if features["spam_check"] else None
                    readability_score = get_readability(email_content) if features["readability"] else None

                    summary = future_summary.result()
                    response = future_response.result() if future_response else ""
                    highlights = future_highlights.result() if future_highlights else ""
                    tone = future_tone.result() if future_tone else ""
                    urgency = future_urgency.result() if future_urgency else ""
                    tasks = future_tasks.result() if future_tasks else ""
                    subject_recommendation = future_subject.result() if future_subject else ""
                    category = future_category.result() if future_category else ""
                    politeness = future_politeness.result() if future_politeness else ""
                    emotion = future_emotion.result() if future_emotion else ""
                    spam_status = future_spam.result() if future_spam else ""

                # Display Results
                st.subheader("📌 Email Summary")
                st.write(summary)

                if features["response"]:
                    st.subheader("✉️ Suggested Response")
                    st.write(response)

                if features["highlights"]:
                    st.subheader("🔑 Key Highlights")
                    st.write(highlights)

                if features["sentiment"]:
                    sentiment = get_sentiment(email_content)
                    sentiment_label = "Positive" if sentiment > 0 else "Negative" if sentiment < 0 else "Neutral"
                    st.subheader("💬 Sentiment Analysis")
                    st.write(f"**Sentiment:** {sentiment_label} (Polarity: {sentiment:.2f})")

                if features["tone"]:
                    st.subheader("🎭 Email Tone")
                    st.write(tone)

                if features["urgency"]:
                    st.subheader("⚠️ Urgency Level")
                    st.write(urgency)

                if features["task_extraction"]:
                    st.subheader("📝 Actionable Tasks")
                    st.write(tasks)

                if features["category"]:
                    st.subheader("📂 Email Category")
                    st.write(category)

                if features["readability"]:
                    st.subheader("📖 Readability Score")
                    st.write(f"{readability_score} / 10")

                if features["export"]:
                    export_data = json.dumps({"summary": summary, "response": response, "highlights": highlights}, indent=4)
                    st.download_button("📥 Download JSON", data=export_data, file_name="analysis.json", mime="application/json")

    except Exception as e:
        st.error(f"❌ Error: {e}")

else:
    st.info("✏️ Paste email content and click 'Generate Insights' to begin.")
