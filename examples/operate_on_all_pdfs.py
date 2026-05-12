import argparse
import askllm
from askllm.extract import Extractor, GetQuestions
from pprint import pprint
from pathlib import Path
import fitz
from tqdm import tqdm

def get_pdf_files(directory: Path):
    return list(directory.rglob("*.pdf"))

def operate_on_path(pdf_path: Path):
    doc = fitz.open(pdf_path)
    texto_completo = ""

    for pagina in doc:
        texto_completo += pagina.get_text()


    extractor = Extractor()
    texto = texto_completo
    resultado = extractor.extract(texto)
    #pprint(resultado)
    get_questions = GetQuestions()
    questions = get_questions(resultado.output)
    return questions, resultado.usage()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf_dir", type=Path)
    args = parser.parse_args()
    pdf_files = get_pdf_files(args.pdf_dir)
    print(f"Found {len(pdf_files)} PDF files.")

    for pdf_file in tqdm(pdf_files[0:5]):
        print(f"Processing {pdf_file}...")
        questions, usage = operate_on_path(pdf_file)
        print(f"Questions for {pdf_file}:")
        pprint(questions)
        print(f"Usage for {pdf_file}:")
        pprint(usage)

if __name__ == "__main__":
    main()