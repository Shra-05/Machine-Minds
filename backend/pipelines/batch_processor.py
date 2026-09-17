from backend.modules.extraction import DataExtractor
from backend.utils.dataset_loader import DatasetLoader
from backend.config import get_db_connection, BATCH_SIZE, DATASET_DIR
from typing import List, Dict
import time

class BatchProcessor:
    def __init__(self):
        self.db = get_db_connection()
        self.collection = self.db['extracted_emails']
    
    def process_and_save_batch(self, emails: List[Dict]) -> Dict:
        """Extract IOCs and save to MongoDB"""
        stats = {
            'processed': 0,
            'success': 0,
            'failed': 0,
            'total_iocs': 0
        }
        
        documents = []
        
        for email_dict in emails:
            try:
                extracted = DataExtractor.extract_email(
                    sender=email_dict.get('sender'),
                    receiver=email_dict.get('receiver'),
                    date=email_dict.get('date'),
                    subject=email_dict.get('subject'),
                    body=email_dict.get('body', ''),
                    dataset_source=email_dict.get('dataset'),
                    label=email_dict.get('label', 0)
                )
                
                doc = {
                    'sender': extracted.sender,
                    'receiver': extracted.receiver,
                    'date': extracted.date,
                    'subject': extracted.subject,
                    'body': extracted.body,
                    'iocs': [
                        {
                            'value': ioc.value,
                            'type': ioc.ioc_type,
                            'source': ioc.source,
                            'extracted_at': ioc.extracted_at
                        }
                        for ioc in extracted.iocs
                    ],
                    'email_hash': extracted.email_hash,
                    'extraction_timestamp': extracted.extraction_timestamp,
                    'dataset_source': extracted.dataset_source,
                    'original_label': extracted.original_label,
                    'confidence': extracted.confidence,
                    'status': 'extracted'
                }
                
                documents.append(doc)
                stats['success'] += 1
                stats['total_iocs'] += len(extracted.iocs)
                
            except Exception as e:
                print(f"  ✗ Failed: {e}")
                stats['failed'] += 1
            
            stats['processed'] += 1
        
        if documents:
            result = self.collection.insert_many(documents)
            print(f"  ✓ Saved {len(result.inserted_ids)} documents to MongoDB")
        
        return stats
    
    def process_all_datasets(self):
        """Process all datasets in batches"""
        print("\n" + "="*70)
        print("STARTING BATCH EXTRACTION PIPELINE")
        print("="*70)
        
        print("\nPHASE 1: Loading datasets...")
        all_emails = DatasetLoader.load_all_datasets(DATASET_DIR)
        print(f"\n✓ Loaded {len(all_emails)} total emails")
        
        print(f"\nPHASE 2: Processing in batches of {BATCH_SIZE}...")
        
        total_stats = {
            'processed': 0,
            'success': 0,
            'failed': 0,
            'total_iocs': 0
        }
        
        start_time = time.time()
        
        for i in range(0, len(all_emails), BATCH_SIZE):
            batch = all_emails[i:i+BATCH_SIZE]
            batch_num = (i // BATCH_SIZE) + 1
            total_batches = (len(all_emails) + BATCH_SIZE - 1) // BATCH_SIZE
            
            print(f"\nBatch {batch_num}/{total_batches}:")
            stats = self.process_and_save_batch(batch)
            
            for key in total_stats:
                total_stats[key] += stats[key]
            
            progress = ((i + BATCH_SIZE) / len(all_emails)) * 100
            print(f"  Progress: {progress:.1f}%")
        
        elapsed = time.time() - start_time
        
        print("\n" + "="*70)
        print("EXTRACTION COMPLETE")
        print("="*70)
        print(f"✓ Processed: {total_stats['processed']}")
        print(f"✓ Success: {total_stats['success']}")
        print(f"✗ Failed: {total_stats['failed']}")
        print(f"✓ Total IOCs extracted: {total_stats['total_iocs']}")
        print(f"⏱ Time elapsed: {elapsed:.1f}s")
        print(f"⚡ Speed: {total_stats['success']/elapsed:.0f} emails/sec")
        
        count = self.collection.count_documents({})
        print(f"\n✓ MongoDB contains {count} extracted emails")

if __name__ == "__main__":
    processor = BatchProcessor()
    processor.process_all_datasets()
