import argparse
import hashlib
import json
import askllm
from askllm.extract import Extractor, GetQuestions
from askllm.models.data import AllAnswers, Answer
from pprint import pformat
from pathlib import Path
import fitz
from tqdm import tqdm

BATCH_SIZE = 5
CACHE_FILE = Path(".llm_cache.json")

def get_pdf_files(directory: Path):
    return list(directory.rglob("*.pdf"))

def load_cache() -> dict:
    if CACHE_FILE.exists():
        with open(CACHE_FILE) as f:
            return json.load(f)
    return {}

def save_cache(cache: dict):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)

def cached_extract(extractor: Extractor, text: str, cache: dict):
    key = hashlib.sha256(text.encode()).hexdigest()
    if key in cache:
        return AllAnswers.model_validate(cache[key]["output"]), None
    resultado = extractor.extract(text)
    cache[key] = {"output": resultado.output.model_dump()}
    save_cache(cache)
    return resultado.output, resultado.usage()

def merge_all_answers(batch_results: list[AllAnswers]) -> AllAnswers:
    merged: dict[str, Answer] = {}
    for result in batch_results:
        for answer in result.answers:
            qid = answer.question_id
            if qid not in merged:
                merged[qid] = answer
            elif answer.answer:
                if merged[qid].answer:
                    merged[qid] = Answer(
                        question_id=qid,
                        answer=True,
                        excerpt=merged[qid].excerpt + " | " + answer.excerpt,
                    )
                else:
                    merged[qid] = answer
    return AllAnswers(answers=list(merged.values()))

def operate_on_path(pdf_path: Path, extractor: Extractor, cache: dict):
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Skipping {pdf_path}: {e}")
        return None, None
    pages = [doc[i].get_text() for i in range(len(doc))]

    get_questions = GetQuestions()

    batches = range(0, len(pages), BATCH_SIZE)
    batch_results = []
    total_usage = None
    for start in tqdm(batches, desc=pdf_path.name, leave=False, position=1):
        batch_text = "".join(pages[start:start + BATCH_SIZE])
        output, usage = cached_extract(extractor, batch_text, cache)
        batch_results.append(output)
        if usage is not None:
            total_usage = usage if total_usage is None else total_usage + usage

    merged = merge_all_answers(batch_results)
    questions = get_questions(merged)
    return questions, total_usage

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf_dir", type=Path)
    parser.add_argument("--output", type=Path, default=Path("results.json"))
    args = parser.parse_args()

    pdf_files = get_pdf_files(args.pdf_dir)
    print(f"Found {len(pdf_files)} PDF files.")

    extractor = Extractor()
    cache = load_cache()
    all_results = {}

    for pdf_file in tqdm(pdf_files, desc="Documents", position=0):
        questions, usage = operate_on_path(pdf_file, extractor, cache)
        if questions is None:
            continue
        all_results[str(pdf_file)] = questions
        tqdm.write(f"\nQuestions for {pdf_file}:")
        tqdm.write(pformat(questions))
        if usage is not None:
            tqdm.write(f"Usage for {pdf_file}:")
            tqdm.write(pformat(usage))

    with open(args.output, "w") as f:
        json.dump(all_results, f, indent=2)
    tqdm.write(f"\nResults saved to {args.output}")

if __name__ == "__main__":
    main()
