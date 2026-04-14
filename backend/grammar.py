def check_grammar(tokens):
    issues = []
    
    # Check for repeated words
    last_word_token = None
    for token in tokens:
        if token["type"] == "WORD":
            if last_word_token and last_word_token["value"].lower() == token["value"].lower():
                issues.append({
                    "type": "REPETITION",
                    "message": f"Repeated word: '{token['value']}'",
                    "line": token["line"],
                    "column": token["column"]
                })
            last_word_token = token
            
    # Check for missing punctuation at the end of text
    # Let's find the last non-whitespace token
    last_meaningful_token = None
    for token in reversed(tokens):
        if token["type"] != "WHITESPACE":
            last_meaningful_token = token
            break
            
    if last_meaningful_token:
        # Look if the last token is punctuation
        if last_meaningful_token["type"] != "PUNCTUATION" or last_meaningful_token["value"] not in {'.', '!', '?'}:
            issues.append({
                "type": "PUNCTUATION",
                "message": "Missing period or punctuation at the end of the input.",
                "line": last_meaningful_token["line"],
                "column": last_meaningful_token["column"] + len(last_meaningful_token["value"])
            })

    # Basic capitalization check for start of sentences...
    # (Leaving this out to focus just on standard rule approach without overcomplicating, as per requirements)

    return issues