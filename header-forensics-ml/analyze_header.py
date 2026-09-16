from email import policy
from email.parser import BytesParser


# --------------------------------
# READ EMAIL
# --------------------------------

with open("Microsoft is hiring!.eml", "rb") as f:
    msg = BytesParser(policy=policy.default).parse(f)


# --------------------------------
# EXTRACT BASIC HEADERS
# --------------------------------

sender = msg.get("From", "")
reply_to = msg.get("Reply-To", "")
return_path = msg.get("Return-Path", "")

authentication = msg.get("Authentication-Results", "")
received_headers = msg.get_all("Received", [])


# --------------------------------
# HELPER FUNCTION
# --------------------------------

def extract_domain(email_address):

    if "@" in email_address:
        return email_address.split("@")[-1].replace(">", "").strip().lower()

    return ""


# --------------------------------
# DOMAINS
# --------------------------------

sender_domain = extract_domain(sender)
reply_domain = extract_domain(reply_to)
return_domain = extract_domain(return_path)


# --------------------------------
# AUTHENTICATION FEATURES
# --------------------------------

spf_pass = 1 if "spf=pass" in authentication.lower() else 0

dkim_pass = 1 if "dkim=pass" in authentication.lower() else 0

dmarc_pass = 1 if "dmarc=pass" in authentication.lower() else 0


# --------------------------------
# REPLY-TO MISMATCH
# --------------------------------

reply_mismatch = 0

if reply_domain and sender_domain:

    if reply_domain != sender_domain:
        reply_mismatch = 1


# --------------------------------
# RETURN-PATH MISMATCH
# --------------------------------

return_mismatch = 0

if return_domain and sender_domain:

    if return_domain != sender_domain:

        # Allow subdomains of sender domain
        if not return_domain.endswith("." + sender_domain):
            return_mismatch = 1


# --------------------------------
# RECEIVED HOPS
# --------------------------------

received_hops = len(received_headers)


# --------------------------------
# BASIC ROUTING CHECK
# --------------------------------

routing_anomaly = 0

if received_hops > 6:
    routing_anomaly = 1


# --------------------------------
# DISPLAY FEATURES
# --------------------------------

print("\n================================")
print("       HEADER ML FEATURES")
print("================================")

print("Sender Domain:", sender_domain)

print("SPF Pass:", spf_pass)

print("DKIM Pass:", dkim_pass)

print("DMARC Pass:", dmarc_pass)

print("Reply-To Mismatch:", reply_mismatch)

print("Return-Path Mismatch:", return_mismatch)

print("Received Hops:", received_hops)

print("Routing Anomaly:", routing_anomaly)