import re

def tokenize(text):
    tokens = []
    # Match words, numbers, spacing, or punctuation separately
    # \b\w+\b for words/numbers
    # \s+ for whitespace
    # [^\w\s] for punctuation
    pattern = re.compile(r'([A-Za-z]+)|([0-9]+)|([^\w\s]+)|(\s+)')
    
    line = 1
    column = 1
    
    for match in pattern.finditer(text):
        token_str = match.group(0)
        
        token_type = "UNKNOWN"
        if match.group(1):
            token_type = "WORD"
        elif match.group(2):
            token_type = "NUMBER"
        elif match.group(3):
            token_type = "PUNCTUATION"
        elif match.group(4):
            token_type = "WHITESPACE"
            
        tokens.append({
            "type": token_type,
            "value": token_str,
            "line": line,
            "column": column
        })
        
        # calculate next line and column
        for char in token_str:
            if char == '\n':
                line += 1
                column = 1
            else:
                column += 1

    return tokens