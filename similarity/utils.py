# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
# from sentence_transformers import SentenceTransformer
# import nltk
# import string
# from nltk.corpus import stopwords
# from nltk.tokenize import word_tokenize
# from nltk.stem import WordNetLemmatizer, PorterStemmer

# # Download necessary NLTK data
# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('wordnet')

# # NLP Preprocessing Setup
# stop_words = set(stopwords.words('english'))
# lemmatizer = WordNetLemmatizer()
# stemmer = PorterStemmer()

# # Load SBERT model for sentence-level semantic similarity
# sbert_model = SentenceTransformer('all-MiniLM-L6-v2')

# def preprocess(text):
#     """Lowercase, remove punctuation, stopwords, lemmatize and stem."""
#     text = text.lower()
#     text = text.translate(str.maketrans('', '', string.punctuation))
#     tokens = word_tokenize(text)

#     cleaned_tokens = []
#     for token in tokens:
#         if token not in stop_words:
#             lemma = lemmatizer.lemmatize(token)
#             stem = stemmer.stem(lemma)
#             cleaned_tokens.append(stem)

#     return ' '.join(cleaned_tokens)

# def get_sbert_embedding(text):
#     """Return SBERT embedding for a given text."""
#     return sbert_model.encode(text)

# def calculate_similarity_score(job_description, transcription, tfidf_weight=0.3, sbert_weight=0.7):
#     """
#     Returns a weighted similarity score between a job description and a transcription.
#     Uses TF-IDF and Sentence-BERT.
#     """
#     # Preprocess for TF-IDF
#     job_description_clean = preprocess(job_description)
#     transcription_clean = preprocess(transcription)

#     # TF-IDF Cosine Similarity
#     tfidf_vectorizer = TfidfVectorizer()
#     tfidf_matrix = tfidf_vectorizer.fit_transform([job_description_clean, transcription_clean])
#     tfidf_similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0][0]

#     # SBERT Embedding Cosine Similarity
#     job_embedding = get_sbert_embedding(job_description)
#     trans_embedding = get_sbert_embedding(transcription)
#     sbert_similarity = cosine_similarity([job_embedding], [trans_embedding])[0][0]

#     # Final Weighted Similarity
#     combined_similarity = (tfidf_weight * tfidf_similarity) + (sbert_weight * sbert_similarity)
#     return round(combined_similarity, 4)






from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer, PorterStemmer
from collections import Counter
import re
import nltk
import string
import numpy as np
import spacy
import joblib
import os
from pathlib import Path

# Create a cache directory if it doesn't exist
CACHE_DIR = Path("similarity/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)
MODEL_CACHE = CACHE_DIR / "sbert_model.joblib"

# Download necessary NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)

# Try to load spaCy model
try:
    nlp = spacy.load('en_core_web_sm')
except:
    # If not available, download the small English model
    import subprocess
    subprocess.call(['python', '-m', 'spacy', 'download', 'en_core_web_sm'])
    nlp = spacy.load('en_core_web_sm')

# NLP Preprocessing Setup
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()
stemmer = PorterStemmer()

# Load SBERT model with caching
def get_sbert_model():
    """Load SBERT model with caching for better performance"""
    if MODEL_CACHE.exists():
        try:
            return joblib.load(MODEL_CACHE)
        except:
            # If loading fails, create a new model
            pass
    
    # Create a new model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Cache it for future use
    try:
        joblib.dump(model, MODEL_CACHE)
    except:
        # If caching fails, just return the model
        pass
    
    return model

# Initialize SBERT model
sbert_model = get_sbert_model()

def get_wordnet_pos(tag):
    """Map POS tag to first character used by WordNet"""
    tag_dict = {
        'J': wordnet.ADJ,
        'N': wordnet.NOUN,
        'V': wordnet.VERB,
        'R': wordnet.ADV
    }
    return tag_dict.get(tag[0].upper(), wordnet.NOUN)

def preprocess(text):
    """Enhanced preprocessing with POS tagging for better lemmatization"""
    # Convert to lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    
    # Remove email addresses
    text = re.sub(r'\S*@\S*\s?', '', text)
    
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Part-of-speech tagging
    pos_tags = nltk.pos_tag(tokens)
    
    cleaned_tokens = []
    for token, tag in pos_tags:
        if token not in stop_words and len(token) > 2:
            # Get the appropriate WordNet POS tag
            wordnet_pos = get_wordnet_pos(tag)
            # Lemmatize with the correct POS tag
            lemma = lemmatizer.lemmatize(token, wordnet_pos)
            cleaned_tokens.append(lemma)
    
    return ' '.join(cleaned_tokens)

def preprocess_spacy(text):
    """More advanced preprocessing using spaCy"""
    doc = nlp(text)
    
    tokens = []
    for token in doc:
        # Keep only tokens that are not stop words, punctuation, or short words
        if not token.is_stop and not token.is_punct and len(token.text) > 2:
            # Use lemmatization from spaCy
            tokens.append(token.lemma_.lower())
    
    return ' '.join(tokens)

def extract_keywords(text, n=20):
    """Extract top keywords from text using TF-IDF"""
    # Preprocess text
    processed_text = preprocess(text)
    
    # Create a single-document "corpus"
    corpus = [processed_text]
    
    # Use TF-IDF to identify important terms
    vectorizer = TfidfVectorizer(max_features=100)
    tfidf_matrix = vectorizer.fit_transform(corpus)
    
    # Get feature names and scores
    feature_names = vectorizer.get_feature_names_out()
    scores = tfidf_matrix.toarray()[0]
    
    # Sort terms by score
    sorted_idx = np.argsort(scores)[::-1]
    
    # Return top n keywords
    return [feature_names[i] for i in sorted_idx[:n]]

def keyword_overlap_score(text1, text2, n=20):
    """Calculate keyword overlap between two texts"""
    # Extract keywords from both texts
    keywords1 = set(extract_keywords(text1, n))
    keywords2 = set(extract_keywords(text2, n))
    
    # Calculate Jaccard similarity
    intersection = keywords1.intersection(keywords2)
    union = keywords1.union(keywords2)
    
    if not union:
        return 0.0
    
    return len(intersection) / len(union)

def get_sbert_embedding(text):
    """Return SBERT embedding for a given text"""
    # For long texts, split into sentences and compute the average embedding
    if len(text) > 512:
        sentences = sent_tokenize(text)
        embeddings = sbert_model.encode(sentences)
        return np.mean(embeddings, axis=0)
    else:
        return sbert_model.encode(text)

def get_chunk_embeddings(text, chunk_size=200, overlap=50):
    """Get embeddings for text chunks to handle long texts better"""
    # Split text into words
    words = text.split()
    
    # Create overlapping chunks
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    
    # If text is very short, just use the original
    if not chunks:
        chunks = [text]
    
    # Get embeddings for each chunk
    embeddings = sbert_model.encode(chunks)
    
    return embeddings

def chunk_similarity(text1, text2, chunk_size=200, overlap=50):
    """Calculate similarity based on best matching chunks"""
    # Get chunk embeddings for both texts
    embeddings1 = get_chunk_embeddings(text1, chunk_size, overlap)
    embeddings2 = get_chunk_embeddings(text2, chunk_size, overlap)
    
    # Calculate cosine similarity between all pairs of chunks
    similarities = cosine_similarity(embeddings1, embeddings2)
    
    # Take the max similarity for each chunk in text1
    max_similarities = np.max(similarities, axis=1)
    
    # Return the average of the max similarities
    return np.mean(max_similarities)

def calculate_similarity_score(job_description, transcription, 
                              tfidf_weight=0.15, 
                              sbert_weight=0.5,
                              keyword_weight=0.2,
                              chunk_weight=0.15):
    """
    Enhanced similarity score calculation with multiple methods:
    1. TF-IDF vectorization with cosine similarity
    2. SBERT sentence embeddings with cosine similarity
    3. Keyword overlap analysis
    4. Chunk-based similarity for better handling of long texts
    
    Returns a weighted similarity score between two texts.
    """
    # Preprocessing
    job_clean = preprocess(job_description)
    trans_clean = preprocess(transcription)
    
    # 1. TF-IDF Similarity
    tfidf_vectorizer = TfidfVectorizer()
    try:
        tfidf_matrix = tfidf_vectorizer.fit_transform([job_clean, trans_clean])
        tfidf_similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0][0]
    except:
        # Handle empty documents or other TF-IDF errors
        tfidf_similarity = 0.0
    
    # 2. SBERT Embedding Similarity
    try:
        job_embedding = get_sbert_embedding(job_description)
        trans_embedding = get_sbert_embedding(transcription)
        sbert_similarity = cosine_similarity([job_embedding], [trans_embedding])[0][0]
    except:
        sbert_similarity = 0.0
    
    # 3. Keyword Overlap Score
    try:
        keyword_sim = keyword_overlap_score(job_description, transcription)
    except:
        keyword_sim = 0.0
    
    # 4. Chunk-based Similarity
    try:
        chunk_sim = chunk_similarity(job_description, transcription)
    except:
        chunk_sim = 0.0
    
    # Calculate weighted similarity
    combined_similarity = (
        tfidf_weight * tfidf_similarity + 
        sbert_weight * sbert_similarity + 
        keyword_weight * keyword_sim +
        chunk_weight * chunk_sim
    )
    
    # Normalize the result to be between 0 and 1
    return round(min(max(combined_similarity, 0.0), 1.0), 4)

def analyze_text_similarity(text1, text2, verbose=False):
    """
    Analyze similarity between two texts in detail.
    Returns a dictionary with multiple similarity metrics.
    """
    # Preprocess texts
    text1_clean = preprocess(text1)
    text2_clean = preprocess(text2)
    
    # Calculate different similarity metrics
    result = {
        "tfidf_similarity": 0.0,
        "sbert_similarity": 0.0,
        "keyword_overlap": 0.0,
        "chunk_similarity": 0.0,
        "combined_score": 0.0,
        "common_keywords": []
    }
    
    # TF-IDF Similarity
    try:
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform([text1_clean, text2_clean])
        result["tfidf_similarity"] = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0][0]
    except:
        pass
    
    # SBERT Similarity
    try:
        text1_embedding = get_sbert_embedding(text1)
        text2_embedding = get_sbert_embedding(text2)
        result["sbert_similarity"] = cosine_similarity([text1_embedding], [text2_embedding])[0][0]
    except:
        pass
    
    # Keyword overlap
    try:
        keywords1 = set(extract_keywords(text1, 20))
        keywords2 = set(extract_keywords(text2, 20))
        common = keywords1.intersection(keywords2)
        result["keyword_overlap"] = len(common) / max(len(keywords1.union(keywords2)), 1)
        result["common_keywords"] = list(common)
    except:
        result["common_keywords"] = []
    
    # Chunk similarity
    try:
        result["chunk_similarity"] = chunk_similarity(text1, text2)
    except:
        pass
    
    # Combined score
    result["combined_score"] = calculate_similarity_score(
        text1, text2,
        tfidf_weight=0.15,
        sbert_weight=0.5,
        keyword_weight=0.2,
        chunk_weight=0.15
    )
    
    return result
