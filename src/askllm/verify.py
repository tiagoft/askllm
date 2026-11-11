"""Check that excerpts quoted by the LLM actually appear in the source text."""

import re
import unicodedata

from rapidfuzz import fuzz

# Characters that PDF extraction and LLMs render inconsistently.
_TRANSLATE = str.maketrans({
    "‘": "'", "’": "'", "“": '"', "”": '"',
    "‐": "-", "‑": "-", "‒": "-", "–": "-", "—": "-", "−": "-",
    "­": "",  # soft hyphen
})
# Calibrated on 839 reports: >= 90 is a real quote (minus PDF artifacts); 70-90 is
# mostly paraphrase or the model's own commentary; < 70 is not in the text.
VERIFIED_THRESHOLD = 90.0
_ELLIPSIS = re.compile(r"\s*(?:\.\.\.|…)\s*")
# Separator used by merge_all_answers when combining excerpts from batches.
MERGE_SEPARATOR = " | "


def normalize(text: str) -> str:
    """Lowercase, NFKC (expands ligatures like 'ﬁ'), undo line-break hyphenation,
    unify quotes/dashes and collapse whitespace."""
    text = unicodedata.normalize("NFKC", text).translate(_TRANSLATE)
    text = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def fragment_score(fragment: str, normalized_source: str) -> float:
    """Score in [0, 100]: 100 for an exact (normalized) substring, otherwise the
    best fuzzy match of the fragment against any window of the source."""
    if fragment in normalized_source:
        return 100.0
    return fuzz.partial_ratio(fragment, normalized_source)


def excerpt_score(excerpt: str, normalized_source: str) -> float | None:
    """Score one excerpt (which may elide text with '...') against the source.

    The excerpt is split on ellipses and each piece is scored separately, so
    legitimately elided quotes are not penalized; the result is the
    length-weighted mean. Returns None for an empty excerpt.
    """
    fragments = [f for f in _ELLIPSIS.split(normalize(excerpt)) if f]
    if not fragments:
        return None
    total = sum(len(f) for f in fragments)
    return sum(fragment_score(f, normalized_source) * len(f) for f in fragments) / total


def merged_excerpt_scores(excerpt: str, normalized_source: str) -> list[float | None]:
    """Score each part of an excerpt merged with MERGE_SEPARATOR."""
    return [excerpt_score(part, normalized_source) for part in excerpt.split(MERGE_SEPARATOR)]
