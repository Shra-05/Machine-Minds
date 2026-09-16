import streamlit as st
import pandas as pd
import joblib
import shap
import re
from email import policy
from email.parser import BytesParser

# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(
    page_title="Header Forensics ML",
    page_icon="🔍",
    layout="centered"
)
# -----------------------------
# Custom UI Styling
# -----------------------------
st.markdown("""
<style>

    /* Main background */
    .stApp {
        background: #0b1020;
    }

    /* Main title */
    h1 {
        font-size: 42px !important;
        font-weight: 700 !important;
        letter-spacing: -1px;
    }

    /* Section headings */
    h2, h3 {
        color: #e8ecf7 !important;
    }

    /* Upload box */
    [data-testid="stFileUploader"] {
        background: #151b2e;
        border: 1px solid #303952;
        border-radius: 14px;
        padding: 15px;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: #151b2e;
        border: 1px solid #303952;
        border-radius: 14px;
        padding: 15px;
    }

    /* Divider */
    hr {
        border-color: #303952;
    }

    /* Warning/info boxes */
    [data-testid="stAlert"] {
        border-radius: 12px;
    }

</style>
""", unsafe_allow_html=True)

st.title("🔍 Header Forensics ML")
st.caption(
    "AI-powered email header analysis • Authentication • Routing • Threat Detection"
)
# -----------------------------
# Load model 
# -----------------------------
saved = joblib.load("model.pkl")
model = saved["model"]
features = saved["features"]

# -----------------------------
# Upload EML
# -----------------------------
uploaded_file = st.file_uploader(
    "Upload Email (.eml)",
    type=["eml"]
)

if uploaded_file is not None:

    # Read email
    msg = BytesParser(
        policy=policy.default
    ).parse(uploaded_file)

    # -----------------------------
    # Header information
    # -----------------------------
    from_address = msg.get("From", "")
    from_domain = from_address.split("@")[-1].strip(">").lower()

    reply_to = msg.get("Reply-To", "")
    reply_domain = reply_to.split("@")[-1].strip(">").lower()

    auth = str(
        msg.get("Authentication-Results", "")
    ).lower()

    # SPF
    spf_feature = (
        1 if "spf=pass" in auth
        else -1 if "spf=fail" in auth
        else 0
    )

    # DKIM
    dkim_feature = (
        1 if "dkim=pass" in auth
        else -1 if "dkim=fail" in auth
        else 0
    )

    # DMARC
    dmarc_feature = (
        1 if "dmarc=pass" in auth
        else -1 if "dmarc=fail" in auth
        else 0
    )

    # Reply-To mismatch
    reply_to_mismatch = (
        1 if reply_domain and reply_domain != from_domain
        else 0
    )

    # Received headers
    num_received_headers = len(
        msg.get_all("Received", [])
    )

    # -----------------------------
    # Body analysis
    # -----------------------------
    body = msg.get_body(
        preferencelist=("plain", "html")
    )

    body_text = body.get_content() if body else ""

    num_urls = (
        body_text.lower().count("http://")
        + body_text.lower().count("https://")
    )

    has_html = (
        1 if msg.get_body(
            preferencelist=("html",)
        ) else 0
    )

    has_attachments = 1 if any(
        part.get_content_disposition() == "attachment"
        for part in msg.walk()
    ) else 0

    contains_tracking_token = 1 if any(
        word in body_text.lower()
        for word in ["utm_", "tracking", "trackid"]
    ) else 0

    num_phone_numbers = len(
        re.findall(
            r"\+?\d[\d\s\-]{8,}\d",
            body_text
        )
    )

    num_emails_in_body = len(
        re.findall(
            r"[\w\.-]+@[\w\.-]+\.\w+",
            body_text
        )
    )

    try:
        x_spam_score = float(
            msg.get("X-Spam-Score", 0)
        )
    except:
        x_spam_score = 0

    list_unsubscribe = (
        1 if msg.get("List-Unsubscribe")
        else 0
    )

    # -----------------------------
    # Feature vector
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

    X = pd.DataFrame(
        [email_features]
    )[features]

    # -----------------------------
    # ML Prediction
    # -----------------------------
    prediction = model.predict(X)[0]
    probabilities = model.predict_proba(X)[0]

    if prediction == 1:
        result = "SUSPICIOUS"
        confidence = probabilities[1]
    else:
        result = "LEGITIMATE"
        confidence = probabilities[0]

    # -----------------------------
    # Result
    # -----------------------------
    st.divider()

    st.subheader("Forensic Result")

    if result == "SUSPICIOUS":
        st.error(
            f"🚨 {result}"
        )
    else:
        st.success(
            f"✅ {result}"
        )

    st.metric(
        "Model Probability",
        f"{confidence * 100:.1f}%"
    )

    # -----------------------------
    # Authentication
    # -----------------------------
    st.subheader("🔐 Authentication")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "SPF",
        "PASS" if spf_feature == 1
        else "FAIL" if spf_feature == -1
        else "UNKNOWN"
    )

    col2.metric(
        "DKIM",
        "PASS" if dkim_feature == 1
        else "FAIL" if dkim_feature == -1
        else "UNKNOWN"
    )

    col3.metric(
        "DMARC",
        "PASS" if dmarc_feature == 1
        else "FAIL" if dmarc_feature == -1
        else "UNKNOWN"
    )

    # -----------------------------
    # Header analysis
    # -----------------------------
    st.subheader("📋 Header Analysis")

    st.write(
        f"**From Domain:** {from_domain}"
    )

    st.write(
        f"**Reply-To:** "
        f"{'MATCH ✓' if not reply_to_mismatch else 'MISMATCH ⚠'}"
    )

    st.write(
        f"**Received Hops:** {num_received_headers}"
    )

    st.write(
        f"**URLs:** {num_urls}"
    )

    st.write(
        f"**Attachments:** "
        f"{'YES' if has_attachments else 'NO'}"
    )

    st.write(
        f"**HTML Email:** "
        f"{'YES' if has_html else 'NO'}"
    )

        # -----------------------------
    # WHY THIS PREDICTION
    # -----------------------------

    st.subheader("🤔 Why was this email flagged?")

    feature_names = {
        "num_urls": "URLs detected",
        "num_phone_numbers": "Phone numbers",
        "num_emails_in_body": "Email addresses in body",
        "num_received_headers": "Received mail hops",
        "has_attachments": "Attachments",
        "has_html": "HTML content",
        "contains_tracking_token": "Tracking token",
        "x_spam_score": "Spam score",
        "list_unsubscribe": "List-Unsubscribe",
        "spf_feature": "SPF authentication",
        "dkim_feature": "DKIM authentication",
        "dmarc_feature": "DMARC authentication",
        "reply_to_mismatch": "Reply-To mismatch"
    }

    # SHAP explanation
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    if isinstance(shap_values, list):
        values = shap_values[prediction][0]
    else:
        values = shap_values

        if len(values.shape) == 3:
            values = values[0, :, prediction]
        elif len(values.shape) == 2:
            values = values[0]

    contributions = []

    for feature, value in zip(features, values):
        contributions.append(
            (feature, float(value))
        )

    contributions.sort(
        key=lambda x: abs(x[1]),
        reverse=True
    )

    # Display top 5 reasons
    for feature, value in contributions[:5]:

        name = feature_names.get(
            feature,
            feature.replace("_", " ").title()
        )

        if value > 0:
            st.markdown(
                f"""
                <div style="
                    background:#321d24;
                    border-left:5px solid #ff4b4b;
                    padding:16px 20px;
                    border-radius:10px;
                    margin:10px 0;
                ">
                    <b style="font-size:17px;">⚠️ {name}</b>
                    <br>
                    <span style="color:#b9becb;">
                        This factor increased the suspicion score.
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

        else:
            st.markdown(
                f"""
                <div style="
                    background:#172b27;
                    border-left:5px solid #21c55d;
                    padding:16px 20px;
                    border-radius:10px;
                    margin:10px 0;
                ">
                    <b style="font-size:17px;">✓ {name}</b>
                    <br>
                    <span style="color:#b9becb;">
                        This factor reduced the suspicion score.
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )