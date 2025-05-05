import streamlit as st
from datetime import date, timedelta
import os
from dotenv import load_dotenv
import google.generativeai as genai

from modules.fx_rates import fetch_fx_rates
from modules.historical_data import fetch_historical_data
from modules.news_aggregation import fetch_news_articles
from modules.indexing import create_faiss_index
from modules.retrieval import retrieve_top_k
from modules.sentiment_analysis import analyze_sentiment
from modules.pdf_summarization import summarize_pdf

# Load environment variables
load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_summary(prompt):
    response = model.generate_content(prompt)
    return response.text

# Streamlit App
st.title("📊 Modular RAG Dashboard")

# FX Rates
st.header("💱 Live FX Rates (Base: INR)")
base_currencies = ["usd", "eur", "jpy", "chf"]
rates = fetch_fx_rates(base_currencies)
st.write(rates)

# Historical Data
st.header("📈 NSE Historical Stock Data")
symbol = st.text_input("Enter Stock Symbol (e.g., TCS)", value="TCS")
start_date = st.date_input("Start Date", value=date.today() - timedelta(days=365))
if st.button("Fetch Historical Data"):
    df = fetch_historical_data(symbol, start_date)
    if not df.empty:
        st.write(df)
        st.line_chart(df.set_index("CH_TIMESTAMP")["CH_CLOSING_PRICE"])
    else:
        st.error("No data found.")

# News Aggregation & RAG
st.header("📰 News Aggregation & RAG Summarization")
query = st.text_input("Enter company or topic", value="TCS")
if st.button("Fetch & Summarize News"):
    articles = fetch_news_articles(query, NEWS_API_KEY)
    if articles:
        index, _ = create_faiss_index(articles)
        top_articles = retrieve_top_k(query, index, articles)
        prompt = f"Summarize the following articles in points:\n\n{''.join(top_articles)}"
        summary = generate_summary(prompt)
        st.write(summary)
    else:
        st.error("No articles found.")

# Sentiment Analysis
st.header("🧠 Sentiment Analysis")
user_input = st.text_area("Enter text for sentiment analysis:")
if st.button("Analyze Sentiment"):
    sentiment, polarity, subjectivity = analyze_sentiment(user_input)
    st.write(f"Sentiment: {sentiment}")
    st.write(f"Polarity: {polarity}")
    st.write(f"Subjectivity: {subjectivity}")

# PDF Summarization
st.header("📄 PDF Summarization")
pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])
if pdf_file is not None:
    if st.button("Summarize PDF"):
        summary = summarize_pdf(pdf_file, generate_summary)
        st.write(summary)
