from validator import DICTIONARY

# ─── Levenshtein Distance ────────────────────────────────────────────────────

def levenshtein(a, b):
    """Compute edit distance between two strings using optimized 1D DP."""
    if a == b:
        return 0
    if len(a) < len(b):
        a, b = b, a          # ensure a is always longer

    if len(b) == 0:
        return len(a)

    previous_row = list(range(len(b) + 1))
    for i, c1 in enumerate(a):
        current_row = [i + 1]
        for j, c2 in enumerate(b):
            insertions  = previous_row[j + 1] + 1
            deletions   = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

# ─── Suggestion Engine ───────────────────────────────────────────────────────

MAX_DISTANCE = 2          # only suggest words within edit distance 2
MAX_LENGTH_DIFF = 2       # skip dict words whose length differs by more than 2
MAX_SUGGESTIONS = 5

def suggest(word):
    """
    Return up to MAX_SUGGESTIONS corrections for `word`.
    - `word` should already be lowercase (normalized).
    - Returns [] if no word within MAX_DISTANCE is found.
    """
    word_len = len(word)
    candidates = []

    for dict_word in DICTIONARY:
        # ── Pre-filter 1: length check (cheap) ─────────────────────────────
        if abs(len(dict_word) - word_len) > MAX_LENGTH_DIFF:
            continue

        # ── Pre-filter 2: first-char match (cheap heuristic) ───────────────
        # Only apply when word is long enough to have a reliable first char
        # (loosens for very short words where typos often hit first char)
        if word_len > 3 and dict_word[0] != word[0]:
            continue

        # ── Levenshtein (expensive) ────────────────────────────────────────
        dist = levenshtein(word, dict_word)

        if dist == 0:
            # Exact match – shouldn't flag this word at all, but guard here
            return []

        if dist <= MAX_DISTANCE:
            candidates.append((dict_word, dist))

    # Sort: primary = distance, secondary = alphabetical for determinism
    candidates.sort(key=lambda x: (x[1], x[0]))
    return [w for w, _ in candidates[:MAX_SUGGESTIONS]]

# ─── Debug Helper ────────────────────────────────────────────────────────────

def suggest_debug(word):
    """Same as suggest() but also returns distance scores for debugging."""
    word_len = len(word)
    candidates = []

    for dict_word in DICTIONARY:
        if abs(len(dict_word) - word_len) > MAX_LENGTH_DIFF:
            continue
        if word_len > 3 and dict_word[0] != word[0]:
            continue
        dist = levenshtein(word, dict_word)
        if dist == 0:
            return []
        if dist <= MAX_DISTANCE:
            candidates.append((dict_word, dist))

    candidates.sort(key=lambda x: (x[1], x[0]))
    return [(w, d) for w, d in candidates[:MAX_SUGGESTIONS]]
