import streamlit as st
import pandas as pd
import requests
from datetime import date, timedelta
import os
from summarizer import summarize_text
from dotenv import load_dotenv
import PyPDF2
import faiss
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from textblob import TextBlob
 # Importing the Gemini API package

# --- Load environment variables ---
load_dotenv()
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "").strip()
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()  # For Gemini API Key

# Validate Gemini API key
if not GEMINI_API_KEY:
    st.error("❌ Invalid or missing Gemini API key.")
    st.stop()

# Set up Gemini client
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')  # or gemini-pro / gemini-1.5-pro
  # Use the Gemini API client

# --- Initialize model ---
embedder = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
  # No .to('cpu')



# --- App Header ---
st.title("📊 NSE & FX Rates Dashboard")
st.markdown("Start date is user-defined. **End date is fixed to 01-01-2025**.")

# --- Section 1: FX Rates ---
# --- Section 1: FX Rates (Embedded Logic) ---
st.header("💱 Live FX Rates (Base: INR)")

BASE_CURRENCIES = ["usd", "eur", "jpy", "chf"]
TARGET = "inr"

def fetch_rates_for(base: str):
    cdn_url = f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{base}.json"
    fallback_url = f"https://latest.currency-api.pages.dev/v1/currencies/{base}.json"

    try:
        res = requests.get(cdn_url, timeout=5)
        data = res.json()
    except:
        try:
            res = requests.get(fallback_url, timeout=5)
            data = res.json()
        except:
            return None

    # Some dated responses may be nested inside base key
    if base in data:
        data = data[base]

    return data.get(TARGET)

# Use embedded fetching logic
try:
    rates = {}
    for base in BASE_CURRENCIES:
        rate = fetch_rates_for(base)
        pair = f"{base.upper()}/{TARGET.upper()}"
        rates[pair] = rate if rate else "Unavailable"

    fx_df = pd.DataFrame(list(rates.items()), columns=["Currency Pair", "Rate"])
    st.dataframe(fx_df.set_index("Currency Pair"), use_container_width=True)

except Exception as e:
    st.error(f"❌ FX rates fetch failed: {str(e)}")

# --- Section 2: NSE Historical Data ---
st.header("📈 NSE Historical Stock Data")
symbol = st.text_input("Enter Stock Symbol (e.g., TCS)", value="TCS")
start_date = st.date_input("Start Date", value=date.today() - timedelta(days=365))

if st.button("Fetch Historical Data"):
    with st.spinner("🔄 Fetching data from Node.js API..."):
        try:
            api_url = "http://localhost:3000/historical"
            params = {"symbol": symbol, "from": start_date.strftime("%d-%m-%Y")}
            response = requests.get(api_url, params=params)
            if response.status_code == 200:
                df = pd.DataFrame(response.json()["data"])
                st.success(f"✅ Fetched {len(df)} records from {start_date} to 01-01-2025.")
                st.dataframe(df)
                st.line_chart(df.set_index("CH_TIMESTAMP")["CH_CLOSING_PRICE"])
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Download CSV", csv, f"{symbol.upper()}_historical.csv", "text/csv")
            else:
                st.error(f"❌ API Error: {response.json().get('error', 'Unknown error')}")
        except Exception as e:
            st.error(f"❌ Failed to fetch data: {str(e)}")

# --- Section 3: News Aggregation & RAG Summarization ---
# --- Section 3: News Aggregation & RAG Summarization ---
st.header("📰 Deal-News Aggregation & RAG Summarization")
company_query = st.text_input("Enter company or topic (e.g., TCS, Infosys)", value="TCS")

if st.button("Fetch & Generate Narrative"):
    try:
        params = {"q": company_query, "apiKey": NEWS_API_KEY, "pageSize": 5, "language": "en"}
        news_response = requests.get("https://newsapi.org/v2/everything", params=params)
        if news_response.status_code != 200:
            st.warning("⚠️ Failed to fetch news.")
        else:
            articles = news_response.json()["articles"]
            corpus = [f"{a['title']}. {a.get('description') or ''}" for a in articles]
            embeddings = embedder.encode(corpus, convert_to_numpy=True)
            index = faiss.IndexFlatL2(embeddings.shape[1])
            index.add(embeddings)
            query_vector = embedder.encode([company_query])
            _, I = index.search(query_vector, k=3)
            top_texts = [corpus[i] for i in I[0]]
            combined_text = "\n".join(top_texts)
            prompt = f"Generate a detailed narrative in points just to get the gist based on the following news articles :\n\n{combined_text}"

            # Call the Gemini API to generate a response
            response = model.generate_content(prompt)

            # Display the synthesized narrative
            st.subheader("🧠 Synthesized Narrative")
            st.markdown(response.text)  # Only show the narrative once here
    except Exception as e:
        st.error(f"❌ Summarization Error: {str(e)}")


# --- Section 4: Sentiment Analysis ---
st.header("🧠 Sentiment Analysis")
user_input = st.text_area("Enter any financial or company update text:")

if st.button("Analyze Sentiment"):
    try:
        # Use TextBlob for sentiment analysis
        blob = TextBlob(user_input)
        sentiment = blob.sentiment

        # Display the sentiment
        st.success(f"🔍 Sentiment: **{sentiment.polarity:.2f}** (Subjectivity: {sentiment.subjectivity:.2f})")

        # Provide interpretation of polarity
        if sentiment.polarity > 0:
            st.info("The sentiment is **positive**.")
        elif sentiment.polarity < 0:
            st.info("The sentiment is **negative**.")
        else:
            st.info("The sentiment is **neutral**.")

    except Exception as e:
        st.error(f"❌ Sentiment analysis failed: {str(e)}")


# --- Section 5: PDF Summarization ---
# --- Section 5: PDF Summarization ---
st.header("📄 PDF Summarization")
pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])

# Define a function to summarize with Gemini
def summarize_with_gemini(text):
    try:
        # Set the prompt for summarization
        prompt = f"Summarize the following PDF content:\n\n{text}"
        response = model.generate_content(prompt)  # Using Gemini API for summarization
        return response.text  # Return the summarized text
    except Exception as e:
        return f"❌ Gemini summarization failed: {str(e)}"

if pdf_file is not None:
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        raw_text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
        st.text_area("Extracted Text", value=raw_text[:2000], height=200)

        if st.button("Summarize PDF"):
            with st.spinner("Summarizing with Gemini..."):
                # Truncate the text to ensure it stays within Gemini's token limits
                summary = summarize_with_gemini(raw_text[:8000])  # Adjust for Gemini token limits
                st.success("📝 Summary:")
                st.write(summary)
    except Exception as e:
        st.error(f"❌ PDF summarization failed: {str(e)}")
