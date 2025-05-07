📊 TaskDone RAG Portal
A unified Retrieval-Augmented Generation (RAG) portal integrating:

💱 Live Currency Exchange Rates

📈 Historical & Real-Time NSE Stock Data

📰 Deal-News Aggregation

🧠 Sentiment Analysis

📄 PDF Summarization

🎯 Synthesized Insights using Gemini

🔗 All accessible from a single web URL — no local installation needed.

👉 Live Demo: [https://iamyourguide.streamlit.app/]
use 
https://taskdone.streamlit.app/

if above link fails

🚀 Features
✅ Unified RAG Interface
Ask natural-language queries like:

"Latest deals, sentiment, FX rates, and earnings for TCS"

The system aggregates news, embeds data using SentenceTransformer, indexes it via FAISS, and synthesizes responses using Gemini-1.5 Flash.
💱 Live Currency Exchange Rates (FX)
Base currency: INR

Pairs supported: USD/INR, EUR/INR, JPY/INR, CHF/INR

Powered by: Fawaz Ahmed Currency API

📈 Historical Stock Data (NSE)
Data sourced from: stock-nse-india API

Input: Stock Symbol (e.g., TCS, INFY)

Download data as CSV

Visualize price trends over time

📊 Real-Time Stock Quotes (Coming Soon)
Plan to ingest CSV-streamed quotes from NSE feed

Auto-refreshing modules for select tickers

📰 Deal-News Aggregation + Summarization
Fetches top news via NewsAPI

Vectorized with SentenceTransformer

Indexed with FAISS

Summarized using Google Gemini API

🧠 Sentiment Analysis
Simple TextBlob-powered analysis

Displays Polarity and Subjectivity

Visual categorization: positive / neutral / negative

📄 PDF Summarization
Upload financial reports, transcripts, etc.

Extracts full text via PyPDF2

Summarized using Gemini-1.5 Flash

Token-safe truncation for long PDFs

🛠 Tech Stack
Tool / Library	Purpose
Streamlit	Web app framework
FAISS	Dense vector indexing & similarity
SentenceTransformer	Embeddings with all-MiniLM-L6-v2
TextBlob	Sentiment Analysis
Gemini API	Summarization & content generation
PyPDF2	PDF Text Extraction
NewsAPI	Deal news aggregation
stock-nse-india	NSE stock data via Node.js backend


🔐 Setup Instructions
1. Clone the Repo

git clone https://github.com/ashutoshbins/taskdone-rag-portal.git
cd taskdone-rag-portal



2. Install Requirements
pip install -r requirements.txt


3. Set Up .env
Create a .env file and add:

HUGGINGFACE_API_KEY=your_huggingface_key
NEWS_API_KEY=your_newsapi_key
GEMINI_API_KEY=your_gemini_api_key


4. Run Node.js Backend for NSE Historical Data
Ensure the Node NSE API is running on port 3000.

5. Launch Streamlit App

streamlit run streamlit_app.py


🔮 Future Enhancements
📊 Real-Time Quote Streaming (CSV Feed from NSE)

🧠 Unified Query Box with multi-module responses

📈 Advanced visualizations with filters and alerts

📄 License
