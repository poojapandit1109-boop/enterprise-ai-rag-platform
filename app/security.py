def detect_prompt_injection(question: str) -> bool:
    """
    Detect common prompt-injection patterns.

    Returns True when the question contains
    a potentially malicious instruction.
    """

    question_lower = question.lower()

    suspicious_patterns = [
        "ignore previous instructions",
        "ignore all previous instructions",
        "ignore the previous instructions",
        "forget previous instructions",
        "forget all previous instructions",
        "system prompt",
        "reveal your instructions",
        "show me your instructions",
        "reveal the system message",
        "bypass your rules",
        "disregard your instructions",
    ]

    for pattern in suspicious_patterns:
        if pattern in question_lower:
            return True

    return False