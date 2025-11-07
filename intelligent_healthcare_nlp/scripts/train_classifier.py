"""Train a simple TF-IDF + Naive Bayes classifier on a small CSV dataset.
Saves pipeline to models/ as a joblib file.
"""
import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import joblib

# Get the script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
data_dir = os.path.join(project_root, 'data')
models_dir = os.path.join(project_root, 'models')

# Create models directory if it doesn't exist
os.makedirs(models_dir, exist_ok=True)

def train():
    # Load the synthetic dataset
    print("Loading training data...")
    data_file = os.path.join(data_dir, 'synthetic_train.csv')
    df = pd.read_csv(data_file)
    print(f"Loaded {len(df)} training examples")

    # Create and train the pipeline
    print("Training model...")
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=1000)),
        ('classifier', MultinomialNB())
    ])

    # Train the model
    pipeline.fit(df['text'], df['label'])
    print("Model training complete")

    # Save the trained pipeline
    model_path = os.path.join(models_dir, 'classifier.joblib')
    print(f"Saving model to: {model_path}")
    joblib.dump(pipeline, model_path)
    print(f"Saved trained model to {model_path}")


if __name__ == '__main__':
    try:
        train()
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
