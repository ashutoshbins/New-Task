import streamlit as st
from datetime import date, timedelta
import os
from dotenv import load_dotenv
import google.generativeai as genai
import plotly.express as px
import plotly.graph_objects as go
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
st.set_page_config(page_title="Modular RAG Dashboard", layout="wide")
st.title("📊 Modular RAG Dashboard")

# FX Rates
st.header("💱 Live FX Rates (Base: INR)")
base_currencies = ["usd", "eur", "jpy", "chf"]
rates = fetch_fx_rates(base_currencies)

# Displaying FX Rates in a styled Plotly table
fig_table = go.Figure(data=[go.Table(
    header=dict(
        values=["<b>Currency Pair</b>", "<b>Rate</b>"],
        fill_color='#1f2c56',  # Dark blue header
        font=dict(color='white', size=14),
        align='left'
    ),
    cells=dict(
        values=[list(rates.keys()), list(rates.values())],
        fill_color='#2c3e50',  # Darker background for cells
        font=dict(color='white', size=12),
        align='left',
        height=30
    ))
])

# Adjust table layout for spacing and full width
fig_table.update_layout(
    margin=dict(t=10, b=10, l=10, r=10),
    width=800,
    paper_bgcolor='#111111',  # Match Streamlit dark background
    plot_bgcolor='#111111'
)

st.plotly_chart(fig_table, use_container_width=True)

# Bar Chart for FX Rates
fig_bar = px.bar(
    x=list(rates.keys()),
    y=list(rates.values()),
    labels={"x": "Currency Pair", "y": "Rate"},
    title="FX Rates (Base: INR)",
    color=list(rates.values()),
    color_continuous_scale='Viridis'
)

# Adjust layout for the bar chart
fig_bar.update_layout(
    margin=dict(t=20, b=20, l=20, r=20),
    xaxis_title="Currency Pair",
    yaxis_title="Rate",
    height=400,
    plot_bgcolor='#111111',
    paper_bgcolor='#111111',
    font=dict(color='white')  # Makes labels readable on dark
)

st.plotly_chart(fig_bar, use_container_width=True)

# Historical Data
st.header("📈 NSE Historical Stock Data")
symbol = st.text_input("Enter Stock Symbol (e.g., TCS)", value="TCS")
start_date = st.date_input("Start Date", value=date.today() - timedelta(days=365))
if st.button("Fetch Historical Data"):
    df = fetch_historical_data(symbol, start_date)
    if not df.empty:
        st.write(df)
        fig = px.line(df, x="CH_TIMESTAMP", y="CH_CLOSING_PRICE", title=f"Closing Prices for {symbol}", labels={"CH_TIMESTAMP": "Date", "CH_CLOSING_PRICE": "Closing Price"})
        st.plotly_chart(fig, use_container_width=True)
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
        prompt = f"Summarize the following articles:\n\n{''.join(top_articles)}"
        summary = generate_summary(prompt)
        st.subheader("RAG Summary")
        st.write(summary)
        st.subheader("Top Retrieved Articles")
        for i, article in enumerate(top_articles):
            st.markdown(f"**{i+1}.** {article}")
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
    sentiment_score = {"Polarity": polarity, "Subjectivity": subjectivity}
    fig = px.bar(x=list(sentiment_score.keys()), y=list(sentiment_score.values()), labels={"x": "Metric", "y": "Value"}, title="Sentiment Metrics")
    st.plotly_chart(fig, use_container_width=True)

# PDF Summarization
st.header("📄 PDF Summarization")
pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])
if pdf_file is not None:
    if st.button("Summarize PDF"):
        summary = summarize_pdf(pdf_file, generate_summary)
        st.subheader("PDF Summary")
        st.write(summary)
