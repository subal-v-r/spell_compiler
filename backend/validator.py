import os

def load_dictionary():
    # Prefer the large dictionary if available
    for path in ["dictionary_large.txt", "dictionary.txt"]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                words = set(w.strip().lower() for w in f if w.strip())
            print(f"[Validator] Loaded {len(words)} words from '{path}'")
            return words
    return set()

DICTIONARY = load_dictionary()

# Ensure common short words are always present
DICTIONARY.update({"i", "a"})

def validate(tokens):
    errors = []

    for i, token in enumerate(tokens):
        if token["type"] == "WORD":
            # Always compare lowercase
            lower_word = token["value"].lower()
            if lower_word not in DICTIONARY:
                errors.append({
                    "word": token["value"],        # preserve original casing for display
                    "normalized": lower_word,      # lowercased for correction lookups
                    "line": token["line"],
                    "column": token["column"],
                    "index": i
                })

    return errors