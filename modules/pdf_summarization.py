from .ingestion import extract_text_from_pdf

def summarize_pdf(pdf_file, summarize_function):
    text = extract_text_from_pdf(pdf_file)
    return summarize_function(text)
