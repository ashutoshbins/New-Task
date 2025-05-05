from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer('all-MiniLM-L6-v2')

def retrieve_top_k(query, index, texts, k=3):
    query_vec = embedder.encode([query])
    _, indices = index.search(query_vec, k)
    return [texts[i] for i in indices[0]]
