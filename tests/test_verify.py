from askllm.verify import excerpt_score, merged_excerpt_scores, normalize

SOURCE = normalize(
    "We trained a classiﬁer on public data.\n"
    "The model may pro-\nduce biased results for under-represented groups.\n"
    "All personal data was anonymised before training."
)


def test_exact_match_despite_pdf_artifacts():
    # ligature, line-break hyphenation and whitespace differences
    assert excerpt_score("We trained a classifier on public data.", SOURCE) == 100
    assert excerpt_score("The model may produce   biased results", SOURCE) == 100


def test_case_and_quotes_ignored():
    assert excerpt_score("ALL PERSONAL DATA WAS ANONYMISED", SOURCE) == 100


def test_unicode_hyphens_ignored():
    # LLMs often emit U+2011 (non-breaking hyphen) where the PDF has '-'
    assert excerpt_score("under‑represented groups", SOURCE) == 100


def test_ellipsis_elision_is_not_penalized():
    assert excerpt_score("We trained a classifier ... anonymised before training.", SOURCE) == 100


def test_fabricated_excerpt_scores_low():
    assert excerpt_score("The authors conducted an ethics board review of the system.", SOURCE) < 70


def test_paraphrase_scores_between():
    score = excerpt_score("The model may produce biased results for minority groups.", SOURCE)
    assert 70 < score < 100


def test_empty_excerpt():
    assert excerpt_score("", SOURCE) is None


def test_merged_parts_scored_separately():
    scores = merged_excerpt_scores(
        "We trained a classifier on public data. | Totally invented sentence about ethics boards.",
        SOURCE,
    )
    assert scores[0] == 100
    assert scores[1] < 70
