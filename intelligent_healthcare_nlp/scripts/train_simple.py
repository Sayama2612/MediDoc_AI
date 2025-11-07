"""Train a simple pipeline model"""
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import joblib

# Sample training data
texts = [
    "Patient prescribed Metformin 500mg twice daily for diabetes management",
    "Chest X-ray reveals no acute cardiopulmonary process",
    "Discharge Summary: Patient stable, continue current medications",
    "Take Lisinopril 10mg once daily with water",
    "MRI shows no evidence of acute infarct or hemorrhage",
    "Patient recovered well after treatment, follow-up in 2 weeks"
]

labels = ["prescription", "report", "summary", "prescription", "report", "summary"]

# Create pipeline
pipeline = Pipeline([
    ('vectorizer', CountVectorizer()),
    ('classifier', MultinomialNB())
])

# Train the model
pipeline.fit(texts, labels)

# Save the pipeline
joblib.dump(pipeline, 'models/simple_classifier.joblib')
print("Model saved successfully")