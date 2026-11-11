import pandas as pd
import json
from tqdm import tqdm
from askllm.models.data import QUESTION_IDS, normalize_question_id
from askllm.verify import VERIFIED_THRESHOLD

QUESTIONS = list(QUESTION_IDS)

def combine_answers(doc: dict) -> dict:
    """Merge entries whose ids normalize to the same question ('1', 'q1', 'Q1').

    Same rule as merge_all_answers: 'yes' if any entry says yes; the excerpt score
    is the best among the entries that agree with that answer.
    """
    combined: dict[str, dict] = {}
    for qid, qdata in doc.items():
        question = normalize_question_id(qid)
        if question is None or qdata.get("answer") is None:
            continue
        combined.setdefault(question, []).append(qdata)
    result = {}
    for question, entries in combined.items():
        answer = any(e["answer"] for e in entries)
        scores = [e.get("excerpt_score") for e in entries if e["answer"] == answer]
        scores = [s for s in scores if s is not None]
        result[question] = {"answer": answer, "excerpt_score": max(scores) if scores else None}
    return result

def ingest():
    with open("results.json", "r") as f:
        data = json.load(f)
        all_entries = []
        for key in tqdm(data.keys()):
            this_entry = {}
            school = key.split("/")[5]
            filename = key.split("/")[-1]
            this_entry["school"] = school
            this_entry["filename"] = filename
            for question, qdata in combine_answers(data[key]).items():
                this_entry[question] = qdata['answer']
                this_entry[f"{question}_score"] = qdata['excerpt_score']
            all_entries.append(this_entry)


    df = pd.DataFrame(all_entries)
    for question in QUESTIONS:
        # Nullable boolean: a question the model never answered stays <NA>
        # (excluded from means) instead of becoming True via bool(NaN).
        df[question] = df.get(question, pd.Series(index=df.index, dtype=object)).astype("boolean")
        missing = df[question].isna().sum()
        if missing:
            print(f"{question}: no answer for {missing} document(s)")
    return df

def apply_excerpt_check(df: pd.DataFrame, threshold: float = VERIFIED_THRESHOLD) -> pd.DataFrame:
    """Return a copy where a 'yes' counts only if its excerpt was found in the document."""
    df = df.copy()
    for question in QUESTIONS:
        score_col = f"{question}_score"
        if score_col not in df.columns:
            continue
        unverified = (df[question].fillna(False) & ~(df[score_col] >= threshold)).astype(bool)
        print(f"{question}: {unverified.sum()} of {df[question].sum()} 'yes' answers lack a verified excerpt")
        df.loc[unverified, question] = False
    return df

def view_results(df: pd.DataFrame):
    # Documents whose Q1 is unknown are excluded along with Q1 == False.
    df_filtered = df[df['Q1'].fillna(False).astype(bool)]
    df_schools = df_filtered.groupby('school')[QUESTIONS].mean()
    df_schools['N'] = df_filtered.groupby('school').size()
    return df_schools

def main():
    df = ingest()
    view_results(df).to_csv("results_summary.csv")
    if df.filter(like="_score").notna().any().any():
        view_results(apply_excerpt_check(df)).to_csv("results_summary_verified.csv")
    else:
        print("No excerpt scores in results.json; rerun operate_on_all_pdfs.py to add them.")


if __name__ == "__main__":
    main()
