import pandas as pd

# Dataset load karna
data = pd.read_csv("dataset/CEAS_08.csv")

# Dataset ki basic information
print("Dataset loaded successfully!")
print("Number of rows:", len(data))
print("Number of columns:", len(data.columns))

print("\nColumn names:")
print(data.columns.tolist())

print("\nFirst 5 rows:")
print(data.head())

print("\nLabel distribution:")
print(data["label"].value_counts())

print("\nURL values:")
print(data["urls"].value_counts().head(10))

print("\nSample email:")
print("Sender:", data["sender"].iloc[0])
print("Subject:", data["subject"].iloc[0])
print("Body:", data["body"].iloc[0][:300])