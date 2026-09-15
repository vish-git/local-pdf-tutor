from functools import lru_cache
from sentence_transformers import SentenceTransformer
MODEL_NAME='sentence-transformers/all-MiniLM-L6-v2'
@lru_cache(maxsize=1)
def get_model(): return SentenceTransformer(MODEL_NAME)
def embed_texts(texts): return get_model().encode(texts, normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)
def embed_query(text): return get_model().encode([text], normalize_embeddings=True, convert_to_numpy=True)
