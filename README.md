# 🔤 Compiler-Based English Spell Checker

> A web-based English spelling identification and correction system built using a **compiler pipeline architecture** — Lexer → Validator → Corrector → Grammar Checker.

---

## 📌 Project Overview

This project implements an **English Spell Checker** that mirrors the internal structure of a compiler to analyze, validate, and correct English text. Instead of compiling source code into machine instructions, this compiler processes natural-language text through well-defined compiler phases to detect spelling errors and suggest corrections.

Users can either **type text directly** or **upload a `.txt` file**. The system returns:
- A list of misspelled words with their positions
- Up to 5 correction suggestions per error (using Levenshtein Distance)
- Grammar issues (repeated words, missing terminal punctuation)
- A fully corrected version of the input text

---

## 🎯 Objectives

1. Apply **compiler design principles** (lexical analysis, semantic validation) to a real-world NLP problem.
2. Build a **modular, extensible pipeline** where each phase is independently maintainable.
3. Implement a **Levenshtein distance–based correction engine** for intelligent, ranked suggestions.
4. Provide a **clean, browser-based UI** requiring no external dependencies for the frontend.
5. Support both **direct text input** and **file upload** for maximum usability.

---

## 🏗️ System Architecture

The backend follows a classical **4-phase compiler pipeline**:

```
Raw Text Input
      │
      ▼
┌─────────────┐
│    LEXER    │  tokenize()  →  Stream of typed tokens
│  (lexer.py) │                 (WORD, NUMBER, PUNCTUATION, WHITESPACE)
└─────────────┘
      │
      ▼
┌───────────────┐
│  VALIDATOR    │  validate()  →  List of spelling errors
│(validator.py) │                 (word, line, column, index)
└───────────────┘
      │
      ▼
┌──────────────┐
│  CORRECTOR   │  suggest()   →  Ranked suggestions per error
│(corrector.py)│                 (Levenshtein Distance ≤ 2)
└──────────────┘
      │
      ▼
┌─────────────┐
│   GRAMMAR   │  check_grammar()  →  Structural issues
│ (grammar.py)│                      (repetitions, missing punctuation)
└─────────────┘
      │
      ▼
  JSON Response  →  Frontend renders errors, suggestions & corrected text
```

---

## ⚙️ Detailed Working of Each Compiler Phase

### Phase 1 — Lexical Analysis (`lexer.py`)

**Goal:** Break raw text into a flat, ordered list of typed tokens.

The `tokenize(text)` function uses a **single compiled regex pattern** to scan the input character-by-character and classify every span into one of four token types:

| Token Type    | Regex Group            | Example       |
|---------------|------------------------|---------------|
| `WORD`        | `[A-Za-z]+`            | `hello`, `The` |
| `NUMBER`      | `[0-9]+`               | `42`, `2024`  |
| `PUNCTUATION` | `[^\w\s]+`             | `.`, `,`, `!` |
| `WHITESPACE`  | `\s+`                  | ` `, `\n`     |

Each token carries metadata:
```json
{ "type": "WORD", "value": "recieve", "line": 1, "column": 5 }
```

Line and column numbers are tracked incrementally so every error can be pinpointed precisely.

---

### Phase 2 — Semantic Validation (`validator.py`)

**Goal:** Check each `WORD` token against a dictionary to flag unknown words.

- Loads `dictionary_large.txt` (~470 k words) into a Python **`set`** at startup for O(1) lookups.
- Comparison is always **case-insensitive** (`lower()`), so `Hello` and `HELLO` are treated identically.
- Produces an error record for every word **not found** in the dictionary:

```json
{
  "word": "recieve",
  "normalized": "recieve",
  "line": 1,
  "column": 5,
  "index": 3
}
```

> **Compiler analogy:** This phase is equivalent to the *symbol-table lookup* in a semantic analyzer — it checks whether identifiers (words) actually exist in the known set of valid symbols (the dictionary).

---

### Phase 3 — Correction Engine (`corrector.py`)

**Goal:** For each misspelled word, find the most similar valid dictionary words.

The `suggest(word)` function applies two cheap pre-filters before computing the expensive edit distance:

1. **Length filter** — skip any dictionary word whose length differs by more than 2.
2. **First-character filter** — for words longer than 3 characters, skip words with a different first letter.

Candidates that pass both filters are scored with **Levenshtein Distance**. The top-5 results (sorted by distance, then alphabetically for determinism) are returned.

---

### Phase 4 — Grammar Checker (`grammar.py`)

**Goal:** Catch lightweight structural/grammatical issues that spelling validation cannot.

Currently detects:

| Rule | Example |
|------|---------|
| **Repeated word** | `"the the cat"` → flags second `the` |
| **Missing terminal punctuation** | Text not ending with `.`, `!`, or `?` |

> **Compiler analogy:** Equivalent to a minimal *syntax analysis* pass, validating structural rules beyond individual token validity.

---

## 🧠 Role of Compiler Design in This Project

| Compiler Concept | Project Implementation |
|---|---|
| Lexical Analysis | `lexer.py` — regex-based tokenizer |
| Symbol Table | `validator.py` — dictionary set for O(1) word lookup |
| Semantic Analysis | `validator.py` — validates token meaning (valid word?) |
| Error Recovery | `corrector.py` — suggests closest valid symbols |
| Syntax / Grammar Rules | `grammar.py` — structural rule checking |
| Intermediate Representation | Token stream (list of dicts) passed between phases |

This architecture ensures **separation of concerns**: each phase can be modified or extended independently without affecting others.

---

## 🔀 Parsing / Tokenization Technique

The lexer uses **maximal-munch tokenization** via Python's `re.compile` + `finditer`:

```python
pattern = re.compile(r'([A-Za-z]+)|([0-9]+)|([^\w\s]+)|(\s+)')
```

- The regex alternation `|` means each match tries groups left-to-right, consuming the **longest possible** span.
- The full input is scanned exactly once — **O(n)** time complexity.
- Whitespace and punctuation tokens are preserved so the **original text can be reconstructed** exactly (for corrected-text generation).

---

## 📐 Levenshtein Distance — The Correction Engine

**Levenshtein Distance** measures the minimum number of single-character edits (insertions, deletions, substitutions) needed to transform one string into another.

### Example

| Operation | String |
|-----------|--------|
| Start | `recieve` |
| Substitute `i`→`e` | `receive` |
| **Edit distance = 1** | |

### Implementation

Uses a **space-optimised 1-D dynamic programming** approach (one row instead of a full matrix):

```python
def levenshtein(a, b):
    previous_row = list(range(len(b) + 1))
    for i, c1 in enumerate(a):
        current_row = [i + 1]
        for j, c2 in enumerate(b):
            insertions     = previous_row[j + 1] + 1
            deletions      = current_row[j] + 1
            substitutions  = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]
```

| Parameter | Value |
|-----------|-------|
| `MAX_DISTANCE` | 2 (only suggest words ≤ 2 edits away) |
| `MAX_LENGTH_DIFF` | 2 (skip words differing in length by > 2) |
| `MAX_SUGGESTIONS` | 5 results returned per error |

---

## 📥 Input Handling

| Method | Details |
|--------|---------|
| **Text box** | User types or pastes text directly into the web UI |
| **File upload** | User uploads a `.txt` file (UTF-8 encoded); content is read server-side |

Both paths converge at the `/compile` POST endpoint in `app.py`, which passes the raw string through all four pipeline phases identically.

---

## 📤 Output Format

The `/compile` endpoint returns a structured JSON response:

```json
{
  "original_text": "I recieve the messege yestarday.",
  "tokens": [
    { "type": "WORD", "value": "I", "line": 1, "column": 1 },
    ...
  ],
  "spelling_errors": [
    {
      "word": "recieve",
      "normalized": "recieve",
      "line": 1,
      "column": 3,
      "index": 2,
      "suggestions": ["receive", "relieve", "retrieve"]
    }
  ],
  "grammar_issues": [
    {
      "type": "PUNCTUATION",
      "message": "Missing period or punctuation at the end of the input.",
      "line": 1,
      "column": 33
    }
  ],
  "corrected_text": "I receive the message yesterday."
}
```

The frontend (`script.js`) renders:
- **Error cards** showing each misspelled word, its position, and clickable suggestions
- **Grammar warnings** with type and position
- **Corrected text** panel where each accepted suggestion replaces the original word in-place

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | [FastAPI](https://fastapi.tiangolo.com/) (Python) | REST API, request routing, pipeline orchestration |
| **Compiler Modules** | Pure Python (`re`, no NLP libraries) | Lexer, Validator, Corrector, Grammar |
| **Dictionary** | `dictionary_large.txt` (~470 k words) | Word validity lookup |
| **Frontend** | HTML5 + Vanilla CSS + Vanilla JS | Browser UI, result rendering |
| **Server** | Uvicorn (ASGI) | High-performance async server |

> No external NLP libraries (NLTK, spaCy, etc.) are used — all language processing is done through custom compiler phases.

---

## 🚀 Setup & Run Instructions

### Prerequisites

- Python 3.9 or higher
- `pip`

### 1. Clone / navigate to the project

```bash
cd spell_compiler
```

### 2. Install dependencies

```bash
pip install fastapi uvicorn python-multipart
```

### 3. Start the server

```bash
cd backend
uvicorn app:app --reload
```

### 4. Open the app

Navigate to **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser.

---

## 💡 Example Input / Output

### Input

```
I recieve the messege yestarday but dint no what to do.
```

### Output — Spelling Errors

| Word | Line | Column | Suggestions |
|------|------|--------|-------------|
| `recieve` | 1 | 3 | `receive`, `relieve` |
| `messege` | 1 | 16 | `message`, `messages` |
| `yestarday` | 1 | 25 | `yesterday` |
| `dint` | 1 | 36 | `dint`, `hint`, `mint` |
| `no` | 1 | 41 | *(valid word — not flagged)* |

### Output — Corrected Text

```
I receive the message yesterday but dint no what to do.
```

### Output — Grammar Issues

*(None — text ends with `.`)*

---

## 🔭 Future Enhancements

| Enhancement | Description |
|---|---|
| **Context-aware corrections** | Use n-gram language models or word embeddings to rank suggestions by contextual probability |
| **BK-Tree indexing** | Replace linear dictionary scan with a BK-Tree for sub-linear nearest-neighbor search |
| **Capitalization rules** | Detect improper capitalization (e.g., mid-sentence capitals, missing sentence-start capitals) |
| **Article grammar** | Flag incorrect article usage (`a` vs. `an`) |
| **Multi-language support** | Swap the dictionary and tokenizer to support other alphabets/languages |
| **REST API documentation** | Auto-generated Swagger UI already available at `/docs` via FastAPI |
| **Downloadable corrected file** | Allow users to download the corrected text as a `.txt` file |
| **Highlight-in-place UI** | Underline errors directly in the input textarea rather than listing them separately |

---

## 📁 Project Structure

```
spell_compiler/
│
├── backend/                        # Python compiler pipeline & API
│   ├── app.py                      # FastAPI app — orchestrator & REST API
│   ├── lexer.py                    # Phase 1: Tokenizer (Lexical Analysis)
│   ├── validator.py                # Phase 2: Spell Validator (Semantic Analysis)
│   ├── corrector.py                # Phase 3: Levenshtein-based suggestion engine
│   ├── grammar.py                  # Phase 4: Grammar rule checker
│   └── dictionary_large.txt        # ~470,000 English words (lookup corpus)
│
├── frontend/                       # Static web interface
│   ├── index.html                  # Single-page application
│   ├── style.css                   # Styles
│   └── script.js                   # API calls & result rendering
│
└── README.md
```

---

## 👨‍💻 Author

**Subal V R**
*April 2026*

---

*Built with ❤️ using compiler theory and Python.*
