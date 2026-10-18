import requests
import json

print("\n" + "="*70)
print("LIVE DEMO: .EML FILE EXTRACTION")
print("="*70 + "\n")

with open('test_phishing.eml', 'rb') as f:
    response = requests.post('http://localhost:8000/api/extract-eml', files={'file': f})

result = response.json()

print(f"✓ File: {result['file']}")
print(f"✓ From: {result['sender']}")
print(f"✓ Subject: {result['subject']}\n")

print(f"EXTRACTION RESULTS:")
print(f"─" * 70)
print(f"IOCs Found: {result['ioc_count']}\n")

for i, ioc in enumerate(result['iocs'], 1):
    print(f"{i}. [{ioc['type'].upper()}] {ioc['value']}")

print(f"\n✓ Email Hash: {result['email_hash'][:20]}...")
print(f"✓ Extraction Time: {result['extraction_timestamp']}")
print(f"✓ Status: {result['status'].upper()}")
print("="*70 + "\n")
