import pandas as pd
import os
from typing import List, Dict

class DatasetLoader:
    @staticmethod
    def load_nigerian_fraud(filepath: str) -> List[Dict]:
        print(f"Loading Nigerian Fraud...")
        df = pd.read_csv(filepath)
        emails = []
        for _, row in df.iterrows():
            emails.append({
                'sender': row['sender'],
                'receiver': row['receiver'],
                'date': row['date'],
                'subject': row['subject'],
                'body': row['body'],
                'label': row['label'],
                'dataset': 'Nigerian_Fraud'
            })
        print(f"  ✓ Loaded {len(emails)} emails")
        return emails
    
    @staticmethod
    def load_phishing_email(filepath: str) -> List[Dict]:
        print(f"Loading Phishing Email...")
        df = pd.read_csv(filepath)
        emails = []
        for _, row in df.iterrows():
            emails.append({
                'sender': None,
                'receiver': None,
                'date': None,
                'subject': None,
                'body': row['text_combined'],
                'label': row['label'],
                'dataset': 'phishing_email'
            })
        print(f"  ✓ Loaded {len(emails)} emails")
        return emails
    
    @staticmethod
    def load_enron(filepath: str) -> List[Dict]:
        print(f"Loading Enron...")
        df = pd.read_csv(filepath)
        emails = []
        for _, row in df.iterrows():
            emails.append({
                'sender': None,
                'receiver': None,
                'date': None,
                'subject': row['subject'],
                'body': row['body'],
                'label': row['label'],
                'dataset': 'Enron'
            })
        print(f"  ✓ Loaded {len(emails)} emails")
        return emails
    
    @staticmethod
    def load_all_datasets(dataset_dir: str) -> List[Dict]:
        all_emails = []
        loaders = {
            'Nigerian_Fraud.csv': DatasetLoader.load_nigerian_fraud,
            'phishing_email.csv': DatasetLoader.load_phishing_email,
            'Enron.csv': DatasetLoader.load_enron,
            'SpamAssasin.csv': DatasetLoader.load_enron,
            'Ling.csv': DatasetLoader.load_enron,
            'Nazario.csv': DatasetLoader.load_enron,
            'CEAS_08.csv': DatasetLoader.load_enron,
        }
        
        for filename, loader in loaders.items():
            filepath = os.path.join(dataset_dir, filename)
            if os.path.exists(filepath):
                try:
                    emails = loader(filepath)
                    all_emails.extend(emails)
                except Exception as e:
                    print(f"  ✗ Error loading {filename}: {e}")
        
        return all_emails
