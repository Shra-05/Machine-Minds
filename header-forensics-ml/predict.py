import pandas as pd
import joblib
import shap
from email import policy
from email.parser import BytesParser
from email.utils import parseaddr

# Load model
saved = joblib.load("model.pkl")
model = saved["model"]
features = saved["features"]

# Read EML
with open("Microsoft is hiring!.eml", "rb") as f:
    msg = BytesParser(policy=policy.default).parse(f)

# -----------------------------
# Header information
# -----------------------------

from_address = msg.get("From", "")
from_domain = from_address.split("@")[-1].strip(">").lower()

reply_to = msg.get("Reply-To", "")
reply_domain = reply_to.split("@")[-1].strip(">").lower()

# Authentication results
auth = str(msg.get("Authentication-Results", "")).lower()

spf_feature = 1 if "spf=pass" in auth else -1 if "spf=fail" in auth else 0
dkim_feature = 1 if "dkim=pass" in auth else -1 if "dkim=fail" in auth else 0
dmarc_feature = 1 if "dmarc=pass" in auth else -1 if "dmarc=fail" in auth else 0

# Reply-To mismatch
reply_to_mismatch = (
    1 if reply_domain and reply_domain != from_domain else 0
)

# Received headers
num_received_headers = len(msg.get_all("Received", []))

# Body
body = msg.get_body(preferencelist=("plain", "html"))

if body:
    body_text = body.get_content()
else:
    body_text = ""

# URLs
num_urls = (
    body_text.lower().count("http://")
    + body_text.lower().count("https://")
)

# HTML
has_html = 1 if msg.get_body(preferencelist=("html",)) else 0

# Attachments
has_attachments = 1 if any(
    part.get_content_disposition() == "attachment"
    for part in msg.walk()
) else 0

# Tracking token
contains_tracking_token = 1 if any(
    word in body_text.lower()
    for word in ["utm_", "tracking", "trackid"]
) else 0

# Phone numbers
import re

num_phone_numbers = len(
    re.findall(r"\+?\d[\d\s\-]{8,}\d", body_text)
)

# Emails in body
num_emails_in_body = len(
    re.findall(r"[\w\.-]+@[\w\.-]+\.\w+", body_text)
)

# Spam score
try:
    x_spam_score = float(msg.get("X-Spam-Score", 0))
except:
    x_spam_score = 0

# List-Unsubscribe
list_unsubscribe = 1 if msg.get("List-Unsubscribe") else 0

# -----------------------------
# Create feature vector
# -----------------------------

email_features = {
    "num_received_headers": num_received_headers,
    "num_urls": num_urls,
    "num_emails_in_body": num_emails_in_body,
    "num_phone_numbers": num_phone_numbers,
    "has_attachments": has_attachments,
    "has_html": has_html,
    "contains_tracking_token": contains_tracking_token,
    "x_spam_score": x_spam_score,
    "list_unsubscribe": list_unsubscribe,
    "spf_feature": spf_feature,
    "dkim_feature": dkim_feature,
    "dmarc_feature": dmarc_feature,
    "reply_to_mismatch": reply_to_mismatch
}

X = pd.DataFrame([email_features])[features]

# -----------------------------
# Prediction
# -----------------------------

prediction = model.predict(X)[0]
probability = model.predict_proba(X)[0]

if prediction == 1:
    result = "SUSPICIOUS"
    confidence = probability[1]
else:
    result = "LEGITIMATE"
    confidence = probability[0]

print("\n===== HEADER FORENSICS RESULT =====")
print("Email       : Microsoft is hiring!.eml")
print("Prediction  :", result)
print("Confidence  :", round(confidence * 100, 2), "%")

print("\n===== FORENSIC FEATURES =====")
print("SPF         :", "PASS" if spf_feature == 1 else "FAIL" if spf_feature == -1 else "UNKNOWN")
print("DKIM        :", "PASS" if dkim_feature == 1 else "FAIL" if dkim_feature == -1 else "UNKNOWN")
print("DMARC       :", "PASS" if dmarc_feature == 1 else "FAIL" if dmarc_feature == -1 else "UNKNOWN")
print("Reply-To    :", "MISMATCH" if reply_to_mismatch else "MATCH")
print("Received    :", num_received_headers, "hops")
print("URLs        :", num_urls)
print("Attachments :", has_attachments)
print("HTML        :", has_html)
# -----------------------------
# SHAP Explanation
# -----------------------------

explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X)

print("\n===== WHY? =====")

# Handle different SHAP output formats
if isinstance(shap_values, list):
    values = shap_values[prediction][0]

else:
    values = shap_values

    # New SHAP versions may return:
    # (samples, features, classes)
    if len(values.shape) == 3:
        values = values[0, :, prediction]

    # Or:
    # (samples, features)
    elif len(values.shape) == 2:
        values = values[0]

# Create feature contributions
contributions = []

for feature, value in zip(features, values):
    value = float(value)
    contributions.append((feature, value))

# Strongest contributions first
contributions.sort(
    key=lambda x: abs(x[1]),
    reverse=True
)

# Display top 5 reasons
for feature, value in contributions[:5]:

    if value > 0:
        print(
            f"+ {feature}: {value:.4f} "
            f"(increased suspicion)"
        )
    else:
        print(
            f"- {feature}: {value:.4f} "
            f"(reduced suspicion)"
        )