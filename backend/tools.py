import re

def limit_lookup(doc_text: str) -> str:
    limits = []
    m1 = re.search(r"per-transaction\s+upi\s+limit\s+is\s+₹\s*([\d,]+)", doc_text, re.IGNORECASE)
    if m1:
        limits.append(f"per-transaction UPI limit is ₹{m1.group(1)}")
    m2 = re.search(r"daily\s+cumulative\s+upi\s+limit\s+across\s+all\s+apps\s+is\s+₹\s*([\d,]+)", doc_text, re.IGNORECASE)
    if m2:
        limits.append(f"daily cumulative UPI limit is ₹{m2.group(1)}")
    m3 = re.search(r"withdraw\s+up\s+to\s+₹\s*([\d,]+)", doc_text, re.IGNORECASE)
    if m3:
        limits.append(f"ATM withdrawal limit is ₹{m3.group(1)}")
    m4 = re.search(r"exceeding\s+₹\s*([\d,]+)", doc_text, re.IGNORECASE)
    if m4:
        limits.append(f"PMLA threshold is ₹{m4.group(1)}")
    if limits:
        return f"Limit(s) found: {', '.join(limits)}"
    return "No specific limit value found in document."

def fee_calculator(doc_text: str) -> str:
    fees = []
    if re.search(r"(?:below|under|less than)\s+(?:₹\s*)?([\d,]+)\s+incur\s+no\s+fee", doc_text, re.IGNORECASE):
        fees.append("NEFT transfers below ₹10,000 incur no fee")
    m = re.search(r"flat\s+fee\s+of\s+(?:₹\s*)?([\d,]+)", doc_text, re.IGNORECASE)
    if m:
        fees.append(f"RTGS flat fee of ₹{m.group(1)}")
    m = re.search(r"incur[s]?\s+(?:a\s+)?(?:flat\s+)?fee\s+of\s+(?:₹\s*)?([\d,]+)", doc_text, re.IGNORECASE)
    if m:
        fees.append(f"Fee of ₹{m.group(1)}")
    if re.search(r"incur\s+no\s+charge", doc_text, re.IGNORECASE):
        fees.append("account closure within 14 days incurs no charge")
    m = re.search(r"(?:₹\s*)?([\d,]+)\s+closure\s+fee", doc_text, re.IGNORECASE)
    if m:
        fees.append(f"closure fee of ₹{m.group(1)}")
    if fees:
        return f"Fee information: {'; '.join(fees)}"
    return "No specific fee information found in document."

def penalty_calculator(doc_text: str) -> str:
    penalties = []
    m = re.search(r"(\d+%)\s+penalty", doc_text, re.IGNORECASE)
    if m:
        penalties.append(f"penalty of {m.group(1)}")
    if penalties:
        return f"Penalty information: {'; '.join(penalties)}"
    return "No specific penalty information found in document."

TOOL_MAP = {
    "limit_lookup": limit_lookup,
    "fee_calculator": fee_calculator,
    "penalty_calculator": penalty_calculator,
}

def route_tool(question: str) -> str:
    q_lower = question.lower()
    if any(word in q_lower for word in ["limit", "per day", "daily", "maximum"]):
        return "limit_lookup"
    if any(word in q_lower for word in ["fee", "charge", "cost", "incurs"]):
        return "fee_calculator"
    if any(word in q_lower for word in ["penalty", "penalize", "premature withdrawal"]):
        return "penalty_calculator"
    return "limit_lookup"
