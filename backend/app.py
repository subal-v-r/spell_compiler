import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from lexer import tokenize
from validator import validate, DICTIONARY
from corrector import suggest, levenshtein, MAX_DISTANCE
from grammar import check_grammar

app = FastAPI(title="Compiler-Based Spell Checker")

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files so index.html, style.css, script.js are available
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    with open("../frontend/index.html", "r", encoding="utf-8") as f:
        return f.read()

def preserve_case(original, replacement):
    """Apply the casing of the original word to the replacement."""
    if original.isupper():
        return replacement.upper()
    if original.istitle() or original[0].isupper():
        return replacement.capitalize()
    return replacement


def generate_corrected_text(tokens, spelling_errors_map):
    """
    Reconstruct the full text, replacing ONLY confirmed misspelled tokens
    with their top suggestion — but ONLY if:
      1. A suggestion exists.
      2. The top suggestion is genuinely different from the original.
      3. The word is not already valid (guard against false positives).
    Everything else is kept verbatim (including whitespace & punctuation).
    """
    corrected_pieces = []

    for i, token in enumerate(tokens):
        original = token["value"]

        if i in spelling_errors_map:
            err = spelling_errors_map[i]
            suggestions = err.get("suggestions", [])

            # Safe-replace: only if we have a suggestion
            if suggestions:
                top = suggestions[0]
                # Double-check: the top suggestion must itself be a valid dictionary word
                if top.lower() in DICTIONARY and top.lower() != original.lower():
                    corrected_pieces.append(preserve_case(original, top))
                    continue

        # Default: keep original token exactly as-is
        corrected_pieces.append(original)

    return "".join(corrected_pieces)

@app.post("/compile")
async def compile_text(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    if file is not None:
        content = await file.read()
        try:
            input_text = content.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="File must be valid UTF-8 text.")
    elif text is not None:
        input_text = text
    else:
        raise HTTPException(status_code=400, detail="Upload a file or provide text.")

    # 1. Lexical Analysis
    tokens = tokenize(input_text)
    
    # 2. Semantic Analysis (Validation)
    errors = validate(tokens)
    
    # 3. Correction Engine (uses normalized lowercase for lookups)
    corrections = []
    spelling_errors_map = {}
    for err in errors:
        # Use the normalized (lowercased) form for Levenshtein matching
        suggestions = suggest(err["normalized"])
        error_detail = {
            "word": err["word"],           # original display form
            "normalized": err["normalized"],
            "line": err["line"],
            "column": err["column"],
            "index": err["index"],
            "suggestions": suggestions
        }
        corrections.append(error_detail)
        spelling_errors_map[err["index"]] = error_detail

    # 4. Light Syntax Phase (Grammar validation)
    grammar_issues = check_grammar(tokens)
    
    # Reconstruct the corrected version
    corrected_text = generate_corrected_text(tokens, spelling_errors_map)

    return {
        "original_text": input_text,
        "tokens": tokens,
        "spelling_errors": corrections,
        "grammar_issues": grammar_issues,
        "corrected_text": corrected_text
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)