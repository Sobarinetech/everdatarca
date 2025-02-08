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
st.set_page_config(page_title="Advanced Email AI", page_icon="📧", layout="wide")
st.title("📨 Advanced Email AI Analysis & Insights")
st.write("Extract insights, generate professional responses, and analyze emails with AI.")

# Default Enabled Features
features = {
    "sentiment": True,
    "highlights": True,
    "response": True,
    "export": True,
    "tone": True,
    "urgency": True,
    "task_extraction": True,
    "subject_recommendation": True,
    "category": True,
    "politeness": True,
    "emotion": True,
    "spam_check": True,
    "readability": True,
    "root_cause": True,  # NEW: Identifies the reason behind tone/sentiment.
    "grammar_check": True,  # NEW: Checks spelling & grammar.
    "clarity": True,  # NEW: Rates clarity of the email.
    "best_response_time": True,  # NEW: Suggests the best time to respond.
    "professionalism": True,  # NEW: Rates professionalism level.
}

# Email Input Section
email_content = st.text_area("📩 Paste your email content here:", height=200)
MAX_EMAIL_LENGTH = 2000  # Increased for better analysis

# Cache AI Responses for Performance
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

# Process Email When Button Clicked
if email_content and st.button("🔍 Generate Insights"):
    try:
        detected_lang = detect(email_content)
        if detected_lang != "en":
            st.error("⚠️ Only English language is supported.")
        else:
            with st.spinner("⚡ Processing email insights..."):
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    # AI-Powered Analysis
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
                    future_root_cause = executor.submit(get_ai_response, "Analyze the root cause of the email tone and sentiment:\n\n", email_content)
                    future_grammar = executor.submit(get_ai_response, "Check spelling & grammar mistakes and suggest fixes:\n\n", email_content)
                    future_clarity = executor.submit(get_ai_response, "Rate the clarity of this email:\n\n", email_content)
                    future_best_time = executor.submit(get_ai_response, "Suggest the best time to respond to this email:\n\n", email_content)
                    future_professionalism = executor.submit(get_ai_response, "Rate the professionalism of this email on a scale of 1-10:\n\n", email_content)

                    # Extract Results
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
                    root_cause = future_root_cause.result()
                    grammar_issues = future_grammar.result()
                    clarity_score = future_clarity.result()
                    best_response_time = future_best_time.result()
                    professionalism_score = future_professionalism.result()
                    readability_score = get_readability(email_content)

                # Display Results
                st.subheader("📌 Email Summary")
                st.write(summary)

                st.subheader("✉️ Suggested Response")
                st.write(response)

                st.subheader("🔑 Key Highlights")
                st.write(highlights)

                st.subheader("💬 Sentiment Analysis")
                sentiment = get_sentiment(email_content)
                sentiment_label = "Positive" if sentiment > 0 else "Negative" if sentiment < 0 else "Neutral"
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

                st.subheader("🧐 Root Cause Analysis")
                st.write(root_cause)

                st.subheader("🔎 Grammar & Spelling Check")
                st.write(grammar_issues)

                st.subheader("🔍 Email Clarity Score")
                st.write(clarity_score)

                st.subheader("🕒 Best Time to Respond")
                st.write(best_response_time)

                st.subheader("🏆 Professionalism Score")
                st.write(f"Rated: {professionalism_score} / 10")

                # Export Options
                export_data = json.dumps({
                    "summary": summary, "response": response, "highlights": highlights,
                    "root_cause": root_cause, "grammar_issues": grammar_issues,
                    "clarity_score": clarity_score, "best_response_time": best_response_time,
                    "professionalism_score": professionalism_score
                }, indent=4)
                st.download_button("📥 Download JSON", data=export_data, file_name="analysis.json", mime="application/json")

    except Exception as e:
        st.error(f"❌ Error: {e}")

else:
    st.info("✏️ Paste email content and click 'Generate Insights' to begin.")
