# import spacy
# import fitz
# from django.conf import settings
# import os

# def parse_cv(pdf_file_path):
#     """
#     Parse CV and extract entities using SpaCy model
#     """
#     try:
#         # Load the SpaCy model
#         model_path = os.path.join(settings.BASE_DIR, 'cv_parser', 'models', 'model-best')
#         nlp = spacy.load(model_path)
        
#         # Extract text from the PDF
#         doc = fitz.open(pdf_file_path)
#         text = ""
#         for page in doc:
#             text += page.get_text()
        
#         # Apply the model to the extracted text
#         doc = nlp(text)
        
#         # Extract and categorize entities
#         entities = {}
#         for ent in doc.ents:
#             if ent.label_ not in entities:
#                 entities[ent.label_] = []
#             entities[ent.label_].append(ent.text)
            
#         return entities
#     except Exception as e:
#         return {"error": str(e)}





# utils.py
import spacy
import fitz
from django.conf import settings
import os

def parse_cv(pdf_file_path):
    """
    Parse CV and extract entities using SpaCy model
    """
    try:
        # Load the SpaCy model
        model_path = os.path.join(settings.BASE_DIR, 'cv_parser', 'models', 'model-best')
        nlp = spacy.load(model_path)
        
        # Extract text from the PDF
        doc = fitz.open(pdf_file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        
        # Apply the model to the extracted text
        doc = nlp(text)
        
        # Extract and categorize entities
        entities = {}
        for ent in doc.ents:
            if ent.label_ not in entities:
                entities[ent.label_] = []
            entities[ent.label_].append(ent.text)
            
        return entities
    except Exception as e:
        return {"error": str(e)}

