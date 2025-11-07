"""Quick synthetic dataset for testing the classifier"""
import pandas as pd
import os

# Get the script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
data_dir = os.path.join(project_root, 'data')

# Create data directory if it doesn't exist
os.makedirs(data_dir, exist_ok=True)

# Create a small synthetic dataset
data = [
    ("Patient prescribed Metformin 500mg twice daily for diabetes management", "prescription"),
    ("Chest X-ray reveals no acute cardiopulmonary process", "report"),
    ("Discharge Summary: Patient stable, continue current medications", "summary"),
    ("Take Lisinopril 10mg once daily with water", "prescription"),
    ("MRI shows no evidence of acute infarct or hemorrhage", "report"),
    ("Patient recovered well after treatment, follow-up in 2 weeks", "summary")
]

df = pd.DataFrame(data, columns=['text', 'label'])
df.to_csv('data/synthetic_train.csv', index=False)
print("Created synthetic dataset at data/synthetic_train.csv")