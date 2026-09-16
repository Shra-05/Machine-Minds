import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import joblib

# Load dataset
df = pd.read_csv("email_dataset_100k.csv")

# 100 legitimate + 100 suspicious
legitimate = df[df["label"] == 0].sample(100, random_state=42)
suspicious = df[df["label"] == 1].sample(100, random_state=42)

data = pd.concat([legitimate, suspicious])

# Convert SPF, DKIM and DMARC results into numbers
def auth_to_number(value):
    value = str(value).lower()
    if "pass" in value:
        return 1
    elif "fail" in value:
        return -1
    return 0

data["spf_feature"] = data["spf_result"].apply(auth_to_number)
data["dkim_feature"] = data["dkim_result"].apply(auth_to_number)
data["dmarc_feature"] = data["dmarc_result"].apply(auth_to_number)

# Reply-To mismatch
data["reply_to_mismatch"] = (
    data["reply_to"].fillna("").str.lower()
    != data["from_domain"].fillna("").str.lower()
).astype(int)

# Features
features = [
    "num_received_headers",
    "num_urls",
    "num_emails_in_body",
    "num_phone_numbers",
    "has_attachments",
    "has_html",
    "contains_tracking_token",
    "x_spam_score",
    "list_unsubscribe",
    "spf_feature",
    "dkim_feature",
    "dmarc_feature",
    "reply_to_mismatch"
]

X = data[features].copy()

# Make everything numeric
for col in features:
    X[col] = pd.to_numeric(X[col], errors="coerce")

X = X.fillna(0)
y = data["label"]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Random Forest
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

# Accuracy
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)

print("Model Accuracy:", round(accuracy * 100, 2), "%")
precision = precision_score(y_test, predictions)
recall = recall_score(y_test, predictions)
f1 = f1_score(y_test, predictions)

cm = confusion_matrix(y_test, predictions)

print("Precision:", round(precision * 100, 2), "%")
print("Recall   :", round(recall * 100, 2), "%")
print("F1 Score :", round(f1 * 100, 2), "%")

print("\nConfusion Matrix:")
print(cm)

# Save model + feature names
joblib.dump(
    {
        "model": model,
        "features": features
    },
    "model.pkl"
)

print("Model saved as model.pkl")