import pandas as pd
import re

# Dataset load karna
data = pd.read_csv("dataset/CEAS_08.csv")

# URL count karne ka function
def count_urls(text):
    if pd.isna(text):
        return 0

    urls = re.findall(r'https?://\S+|www\.\S+', str(text))
    return len(urls)

# URL count feature banana
data["url_count"] = data["body"].apply(count_urls)

# Result check karna
print("Feature extraction successful!")

print("\nSample URL counts:")
print(data[["body", "url_count", "label"]].head(10))

# Suspicious keywords ki list
suspicious_keywords = [
    "urgent",
    "verify",
    "verification",
    "password",
    "account",
    "click",
    "login",
    "bank",
    "confirm",
    "winner",
    "congratulations",
    "security",
    "update"
]

# Suspicious keywords count karne ka function
def count_suspicious_keywords(row):
    text = str(row["subject"]) + " " + str(row["body"])
    text = text.lower()

    count = 0

    for keyword in suspicious_keywords:
        count += text.count(keyword)

    return count

# Feature create karna
data["suspicious_keyword_count"] = data.apply(
    count_suspicious_keywords,
    axis=1
)

# Result check karna
print("\nSuspicious keyword feature:")
print(
    data[
        ["subject", "suspicious_keyword_count", "label"]
    ].head(10)
)

# Suspicious sender domain words
suspicious_sender_words = [
    "paypa1",
    "verify",
    "security",
    "account",
    "login"
]

# Sender suspicious hai ya nahi check karna
def check_sender(row):
    sender = str(row["sender"]).lower()

    for word in suspicious_sender_words:
        if word in sender:
            return 1

    return 0

# Feature create karna
data["sender_suspicious"] = data.apply(
    check_sender,
    axis=1
)

# Result check karna
print("\nSender suspicion feature:")
print(
    data[
        ["sender", "sender_suspicious", "label"]
    ].head(10)
)

# Email body length feature
data["body_length"] = data["body"].fillna("").astype(str).str.len()

# Result check karna
print("\nEmail body length feature:")
print(
    data[
        ["body_length", "label"]
    ].head(10)
)

print("\nFinal features:")
print(
    data[
        [
            "url_count",
            "suspicious_keyword_count",
            "sender_suspicious",
            "body_length",
            "label"
        ]
    ].head(10)
)

print("\nMissing values:")
print(
    data[
        [
            "url_count",
            "suspicious_keyword_count",
            "sender_suspicious",
            "body_length",
            "label"
        ]
    ].isnull().sum()
)

# Final features ko CSV file me save karna
data[
    [
        "url_count",
        "suspicious_keyword_count",
        "sender_suspicious",
        "body_length",
        "label"
    ]
].to_csv("dataset/artifact_features.csv", index=False)

print("\nFeature dataset saved successfully!")