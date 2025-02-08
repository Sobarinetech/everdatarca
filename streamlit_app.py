import streamlit as st
import google.generativeai as genai
from langdetect import detect
from textblob import TextBlob
from fpdf import FPDF
from io import BytesIO
import concurrent.futures
import json

# Configure API Key securely from Streamlit's secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Streamlit App Configuration
st.set_page_config(page_title="Fast Email Storytelling AI", page_icon="📧", layout="wide")
st.title("📨 Lightning-Fast Email Storytelling AI")
st.write("Extract insights, generate professional responses, and analyze emails in real-time.")

# Features enabled by default
features = {feature: True for feature in [
    "sentiment", "highlights", "response", "export", "tone", "urgency",
    "task_extraction", "subject_recommendation", "category", "politeness",
    "emotion", "spam_check", "readability"
]}

# Email Input Section
email_content = st.text_area("📩 Paste your email content here:", height=200)

MAX_EMAIL_LENGTH = 2000

@st.cache_data(ttl=3600)
def get_ai_response(prompt, email_content):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt + email_content[:MAX_EMAIL_LENGTH])
        return response.text.strip()
    except Exception as e:
        st.error(f"AI Error: {e}")
        return ""

def get_sentiment(email_content):
    return TextBlob(email_content).sentiment.polarity

def get_readability(email_content):
    return round(TextBlob(email_content).sentiment.subjectivity * 10, 2)

def export_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    return pdf.output(dest='S').encode('latin1')

if email_content and st.button("🔍 Generate Insights"):
    try:
        detected_lang = detect(email_content)
        if detected_lang != "en":
            st.error("⚠️ Only English language is supported.")
        else:
            with st.spinner("⚡ Processing email insights..."):
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future_summary = executor.submit(get_ai_response, "Summarize this email concisely:\n\n", email_content)
                    future_response = executor.submit(get_ai_response, "Draft a professional response:\n\n", email_content)
                    future_highlights = executor.submit(get_ai_response, "Highlight key points:\n\n", email_content)
                    future_tone = executor.submit(get_ai_response, "Detect the tone of this email:\n\n", email_content)
                    future_urgency = executor.submit(get_ai_response, "Analyze urgency level:\n\n", email_content)
                    future_tasks = executor.submit(get_ai_response, "List actionable tasks:\n\n", email_content)
                    future_subject = executor.submit(get_ai_response, "Suggest a professional subject line:\n\n", email_content)
                    future_category = executor.submit(get_ai_response, "Categorize this email:\n\n", email_content)
                    future_politeness = executor.submit(get_ai_response, "Evaluate politeness score:\n\n", email_content)
                    future_emotion = executor.submit(get_ai_response, "Analyze emotions in this email:\n\n", email_content)
                    future_spam = executor.submit(get_ai_response, "Detect if this email is spam/scam:\n\n", email_content)
                    readability_score = get_readability(email_content)

                    summary = future_summary.result()
                    response = future_response.result()
                    highlights = future_highlights.result()
                    tone = future_tone.result()
                    urgency = future_urgency.result()
                    tasks = future_tasks.result()
                    subject_recommendation = future_subject.result()
                    category = future_category.result()
                    politeness = future_politeness.result()
                    emotion = future_emotion.result()
                    spam_status = future_spam.result()

                st.subheader("📌 Email Summary")
                st.write(summary)

                st.subheader("✉️ Suggested Response")
                st.write(response)

                st.subheader("🔑 Key Highlights")
                st.write(highlights)

                sentiment = get_sentiment(email_content)
                sentiment_label = "Positive" if sentiment > 0 else "Negative" if sentiment < 0 else "Neutral"
                st.subheader("💬 Sentiment Analysis")
                st.write(f"**Sentiment:** {sentiment_label} (Polarity: {sentiment:.2f})")

                st.subheader("🎭 Email Tone")
                st.write(tone)

                st.subheader("⚠️ Urgency Level")
                st.write(urgency)

                st.subheader("📝 Actionable Tasks")
                st.write(tasks)

                st.subheader("📂 Email Category")
                st.write(category)

                st.subheader("📖 Readability Score")
                st.write(f"{readability_score} / 10")

                export_data = json.dumps({
                    "summary": summary, "response": response, "highlights": highlights
                }, indent=4)
                st.download_button("📥 Download JSON", data=export_data, file_name="analysis.json", mime="application/json")
    except Exception as e:
        st.error(f"❌ Error: {e}")
else:
    st.info("✏️ Paste email content and click 'Generate Insights' to begin.")
