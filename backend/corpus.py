DOCUMENTS = {
    "doc_upi": {
        "title": "UPI Transfer Limits",
        "text": "Per-transaction UPI limit is ₹1,00,000. Daily cumulative UPI limit across all apps is ₹2,00,000 for verified accounts.",
        "keywords": ["upi", "transfer", "limit", "cumulative"]
    },
    "doc_neft": {
        "title": "NEFT/RTGS Charges",
        "text": "NEFT transfers below ₹10,000 incur no fee. RTGS is available only for transfers above ₹2,00,000 and incurs a flat fee of ₹25.",
        "keywords": ["neft", "rtgs", "fee", "charge", "transfer"]
    },
    "doc_atm": {
        "title": "ATM Withdrawal Limits",
        "text": "Savings account holders can withdraw up to ₹40,000 per day from ATMs, subject to a maximum of 5 free transactions per month at other-bank ATMs.",
        "keywords": ["atm", "withdrawal", "limit", "savings", "transaction"]
    },
    "doc_pmla": {
        "title": "PMLA Reporting Threshold",
        "text": "Cash transactions equal to or exceeding ₹10,00,000 in a single transaction or a series of connected transactions must be reported as per PMLA guidelines.",
        "keywords": ["pmla", "reporting", "threshold", "cash", "transaction"]
    },
    "doc_fd": {
        "title": "Fixed Deposit Premature Withdrawal",
        "text": "Premature withdrawal of a fixed deposit before maturity incurs a 1% penalty on the applicable interest rate.",
        "keywords": ["fixed deposit", "premature", "withdrawal", "penalty", "fd"]
    },
    "doc_closure": {
        "title": "Account Closure Charges",
        "text": "Accounts closed within 14 days of opening incur no charge. Accounts closed between 14 days and 1 year incur a ₹500 closure fee.",
        "keywords": ["account", "closure", "charge", "fee", "closed"]
    }
}

def get_doc(doc_id: str) -> dict:
    doc = DOCUMENTS.get(doc_id)
    if doc is None:
        raise ValueError(f"Unknown document id: {doc_id}")
    return {"doc_id": doc_id, "title": doc["title"], "text": doc["text"]}

def search_documents(question: str) -> dict:
    q_lower = question.lower()
    best_doc_id = None
    best_score = -1

    for doc_id, doc in DOCUMENTS.items():
        score = 0
        for kw in doc["keywords"]:
            if kw in q_lower:
                score += 1
        if any(word in doc["title"].lower() for word in q_lower.split()):
            score += 2
        if any(word in doc["text"].lower() for word in q_lower.split()):
            score += 1
        if score > best_score:
            best_score = score
            best_doc_id = doc_id

    if best_doc_id is None:
        best_doc_id = "doc_upi"

    return get_doc(best_doc_id)
