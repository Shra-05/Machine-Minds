import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Feature dataset load karna
data = pd.read_csv("dataset/artifact_features.csv")

# Features
X = data[
    [
        "url_count",
        "suspicious_keyword_count",
        "sender_suspicious",
        "body_length"
    ]
]

# Target
y = data["label"]

# Training aur testing data split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("Data split successful!")
print("Total samples:", len(data))
print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))

# Random Forest model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

# Model train karna
model.fit(X_train, y_train)

print("\nModel training successful!")

# Test data par prediction
y_pred = model.predict(X_test)

# Accuracy calculate karna
accuracy = accuracy_score(y_test, y_pred)

print("Model Accuracy:", round(accuracy * 100, 2), "%")

# Trained model save karna
joblib.dump(model, "model/artifact_model.pkl")

print("Model saved successfully!")