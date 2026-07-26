CASES = [
    {
        "id": "case_pass",
        "question": "What is the daily UPI transfer limit?",
        "rigging": {},
        "correct_doc": "doc_upi",
        "correct_tool": "limit_lookup",
        "expected_keywords": ["2,00,000", "UPI"]
    },
    {
        "id": "case_bad_search",
        "question": "What is the daily UPI transfer limit?",
        "rigging": {"doc_override": "doc_atm"},
        "correct_doc": "doc_upi",
        "correct_tool": "limit_lookup",
        "expected_keywords": ["2,00,000", "UPI"]
    },
    {
        "id": "case_bad_tool",
        "question": "What fee applies to an NEFT transfer under rupees 10000?",
        "rigging": {"tool_override": "penalty_calculator"},
        "correct_doc": "doc_neft",
        "correct_tool": "fee_calculator",
        "expected_keywords": ["no fee", "NEFT"]
    },
    {
        "id": "case_bad_generation",
        "question": "What is the penalty for premature FD withdrawal?",
        "rigging": {"inject_bug": True},
        "correct_doc": "doc_fd",
        "correct_tool": "penalty_calculator",
        "expected_keywords": ["1%", "penalty"]
    },
    {
        "id": "case_ambiguous",
        "question": "What is the ATM withdrawal limit per day?",
        "rigging": {"doc_override": "doc_neft", "tool_override": "fee_calculator"},
        "correct_doc": "doc_atm",
        "correct_tool": "limit_lookup",
        "expected_keywords": ["40,000", "ATM"]
    },
]

def get_case(case_id: str) -> dict:
    for c in CASES:
        if c["id"] == case_id:
            return c
    raise ValueError(f"Unknown case id: {case_id}")
