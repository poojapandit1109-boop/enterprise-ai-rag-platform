def detect_prompt_injection(question: str) -> bool:
    """
    Detect common prompt-injection patterns.

    Returns True when the question contains a potentially
    malicious instruction.

    Note:
        This is a basic pattern-based detector, not a complete
        prompt-injection defense.
    """

    if not isinstance(question, str) or not question.strip():
        return False

    question_lower = question.lower()

    suspicious_patterns = [
        # Instruction override attempts
        "ignore previous instructions",
        "ignore all previous instructions",
        "ignore the previous instructions",
        "ignore all security rules",
        "ignore all security policies",
        "forget previous instructions",
        "forget all previous instructions",
        "disregard your instructions",
        "disregard all security rules",

        # System prompt and instruction extraction
        "system prompt",
        "reveal your instructions",
        "show me your instructions",
        "reveal the system message",
        "reveal confidential instructions",
        "show confidential system instructions",
        "confidential system instructions",

        # Rule bypass attempts
        "bypass your rules",
        "bypass security rules",
        "bypass all security rules",
        "override your instructions",
        "override system instructions",
    ]

    for pattern in suspicious_patterns:
        if pattern in question_lower:
            return True

    return False
