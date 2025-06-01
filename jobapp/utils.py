# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
# import torch
# from transformers import BertTokenizer, BertModel

# # Load BERT model and tokenizer for sentence embeddings
# tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
# model = BertModel.from_pretrained('bert-base-uncased')

# def get_bert_embedding(text):
#     """ Generate BERT embeddings for a given text """
#     inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
#     with torch.no_grad():
#         outputs = model(**inputs)
#     # Use the embeddings of the [CLS] token (first token)
#     return outputs.last_hidden_state[:, 0, :].squeeze().numpy()

# def calculate_similarity_score(job_description, transcription):
#     # TF-IDF Similarity
#     documents = [job_description, transcription]
    
#     # Use TF-IDF to vectorize the text
#     vectorizer = TfidfVectorizer(stop_words='english')
#     tfidf_matrix = vectorizer.fit_transform(documents)
    
#     # Calculate cosine similarity between the job description and the transcription using TF-IDF
#     tfidf_similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0][0]
    
#     # BERT Similarity
#     job_description_embedding = get_bert_embedding(job_description)
#     transcription_embedding = get_bert_embedding(transcription)
    
#     # Calculate cosine similarity between BERT embeddings
#     bert_similarity = cosine_similarity([job_description_embedding], [transcription_embedding])[0][0]
    
#     # Combine the two similarity scores (you can adjust the weight of each if desired)
#     combined_similarity_score = 0.5 * tfidf_similarity + 0.5 * bert_similarity
    
#     # Return the combined similarity score (a value between 0 and 1)
#     return combined_similarity_score


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