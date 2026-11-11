"""Convert the per-school summaries written by view_results.py into LaTeX tables.

Run from the directory holding the CSVs (same as view_results.py):
    python examples/summary_to_latex.py
Writes results_summary.tex and, if present, results_summary_verified.tex.
Requires \\usepackage{booktabs} in the document.
"""
import re
from pathlib import Path

import pandas as pd
import toml

from askllm.verify import VERIFIED_THRESHOLD

QUESTIONS_FILE = Path(__file__).parent.parent / "src" / "askllm" / "resources" / "questions.toml"
TABLE_QUESTIONS = [f"Q{i}" for i in range(2, 10)]  # Q1 is the filter, always 1.0
# Wording fixes for print only; the prompt itself is left unchanged.
PRINT_FIXES = {"Artifical": "Artificial", "Project": "project", "or explains": "or explain"}

CAPTION = "Proportion of AI-focused reports (Q1 = yes) that address each question, by institution"
TABLES = [
    ("results_summary.csv", "results_summary.tex", "tab:results-summary", CAPTION + "."),
    ("results_summary_verified.csv", "results_summary_verified.tex", "tab:results-summary-verified",
     CAPTION + ", counting a ``yes'' only when its supporting excerpt was found in the report "
     rf"(fuzzy-match score $\geq {VERIFIED_THRESHOLD:g}$)."),
]


def load_questions() -> dict[str, str]:
    prompt = toml.load(QUESTIONS_FILE)["prompt"]
    questions = {}
    for qid, text in re.findall(r"^(Q[1-9])\s+(.+?)\s*$", prompt, flags=re.M):
        for wrong, right in PRINT_FIXES.items():
            text = text.replace(wrong, right)
        questions[qid] = text
    return questions


def to_latex(df: pd.DataFrame, caption: str, label: str, questions: dict[str, str]) -> str:
    rows = "\n".join(
        "    " + str(school).replace("_", r"\_") + f" & {int(r.N)} & "
        + " & ".join(f"{r[q]:.2f}" for q in TABLE_QUESTIONS) + r" \\"
        for school, r in df.iterrows()
    )
    legend = "\n".join(f"      {qid} & {text} \\\\" for qid, text in questions.items())
    return rf"""\begin{{table}}[htbp]
  \centering
  \small
  \setlength{{\tabcolsep}}{{5pt}}
  \caption{{{caption}}}
  \label{{{label}}}
  \begin{{tabular}}{{l r {"c" * len(TABLE_QUESTIONS)}}}
    \toprule
    Institution & $N$ & {" & ".join(TABLE_QUESTIONS)} \\
    \midrule
{rows}
    \bottomrule
  \end{{tabular}}

  \medskip
  \begin{{minipage}}{{\linewidth}}
    \footnotesize
    \begin{{tabular}}{{@{{}}l p{{0.9\linewidth}}@{{}}}}
{legend}
    \end{{tabular}}
  \end{{minipage}}
\end{{table}}
"""


def main():
    questions = load_questions()
    for csv, tex, label, caption in TABLES:
        if not Path(csv).exists():
            print(f"Skipping {tex}: {csv} not found")
            continue
        df = pd.read_csv(csv, index_col=0)
        Path(tex).write_text(to_latex(df, caption, label, questions))
        print(f"Wrote {tex}")


if __name__ == "__main__":
    main()
