"""Simple extractive summarization using sentence scoring."""
import re
from collections import defaultdict
import numpy as np

def preprocess_text(text):
    # Remove special characters and digits
    formatted_text = re.sub('[^a-zA-Z\s.]', ' ', text)
    formatted_text = re.sub('\s+', ' ', formatted_text)
    return formatted_text

def sentence_similarity(sent1, sent2):
    # Convert sentences to sets of words
    words1 = set(sent1.lower().split())
    words2 = set(sent2.lower().split())
    
    # Calculate Jaccard similarity
    if not words1 or not words2:
        return 0
    return len(words1 & words2) / len(words1 | words2)

def summarize(text: str, max_sentences: int = 3) -> str:
    """Create an extractive summary by selecting the most important sentences."""
    if not text or not text.strip():
        return "No text provided"
        
    # Split into sentences (simple split on period)
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    if not sentences:
        return text
        
    # If text is short, return as is
    if len(sentences) <= max_sentences:
        return text
        
    # Preprocess
    cleaned_sentences = [preprocess_text(sent) for sent in sentences]
    
    # Calculate sentence scores based on similarity with other sentences
    scores = defaultdict(float)
    for i, sent1 in enumerate(cleaned_sentences):
        for sent2 in cleaned_sentences:
            if sent1 != sent2:
                scores[i] += sentence_similarity(sent1, sent2)
                
    # Get indices of top scoring sentences (maintaining original order)
    ranked_indices = sorted(range(len(sentences)), 
                          key=lambda i: scores[i], 
                          reverse=True)[:max_sentences]
    ranked_indices = sorted(ranked_indices)  # Preserve original order
    
    # Combine sentences
    summary = '. '.join(sentences[i] for i in ranked_indices)
    if not summary.endswith('.'):
        summary += '.'
        
    return summary
		except Exception:
			return text[:max_length] + ('...' if len(text) > max_length else '')
	res = SUMMARIZER(text, max_length=max_length, min_length=30, do_sample=False)
	return res[0]['summary_text']