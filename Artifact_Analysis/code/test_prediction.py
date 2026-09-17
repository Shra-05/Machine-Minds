import pandas as pd
import joblib

# Saved model load karna
model = joblib.load("model/artifact_model.pkl")

# Feature dataset load karna
data = pd.read_csv("dataset/artifact_features.csv")

# Ek email ka features lena
sample = data[
    [
        "url_count",
        "suspicious_keyword_count",
        "sender_suspicious",
        "body_length"
    ]
].iloc[[0]]

# Prediction
prediction = model.predict(sample)[0]

# Confidence score
probabilities = model.predict_proba(sample)[0]
confidence = max(probabilities) * 100

# Result
if prediction == 1:
    result = "Phishing"
else:
    result = "Legitimate"

print("Prediction:", result)
print("Confidence Score:", round(confidence, 2), "%")
