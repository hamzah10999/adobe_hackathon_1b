#!/usr/bin/env python3
import json
import os
import re
import time
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass

import fitz  # PyMuPDF
from llama_cpp import Llama
from rank_bm25 import BM25Okapi
import nltk
from nltk.tokenize import word_tokenize

# Ensure NLTK data is available
nltk.download('punkt', quiet=True)

@dataclass
class Config:
    model_path: str = "./models/tinyllama-1.1b-chat-v1.0.Q4_0.gguf"
    context_length: int = 1024
    max_tokens: int = 256
    temperature: float = 0.0
    n_threads: int = 4
    n_batch: int = 256
    min_section_length: int = 150
    max_chunks: int = 5

class DocumentProcessor:
    def __init__(self, config: Config):
        self.config = config
        self.llm = Llama(
            model_path=config.model_path,
            n_ctx=config.context_length,
            n_threads=config.n_threads,
            n_batch=config.n_batch,
            verbose=False
        )

    def extract_text_chunks(self, pdf_path: str) -> List[Dict[str, Any]]:
        print(f"[STATUS] Extracting chunks from {Path(pdf_path).name}")
        doc = fitz.open(pdf_path)
        chunks = []
        for page_num in range(len(doc)):
            text = doc[page_num].get_text()
            if len(text.strip()) < self.config.min_section_length:
                continue
            sections = re.split(r'\n\s*\n', text)
            for sec in sections:
                section = sec.strip()
                if len(section) >= self.config.min_section_length:
                    chunks.append({
                        'text': section,
                        'page': page_num + 1,
                        'document': Path(pdf_path).name
                    })
        doc.close()
        print(f"[STATUS] Found {len(chunks)} chunks in {Path(pdf_path).name}")
        return chunks

    def rank_chunks(self, chunks: List[Dict], persona: str, job: str) -> List[Dict]:
        print(f"[STATUS] Ranking {len(chunks)} chunks by relevance")
        query_tokens = word_tokenize(f"{persona} {job}".lower())
        tokenized = [word_tokenize(c['text'].lower()) for c in chunks]
        if not tokenized:
            return []
        bm25 = BM25Okapi(tokenized)
        scores = bm25.get_scores(query_tokens)
        for c, s in zip(chunks, scores):
            c['score'] = s
        ranked = sorted(chunks, key=lambda x: x['score'], reverse=True)
        selected = ranked[:self.config.max_chunks * 2]
        print(f"[STATUS] Selected top {len(selected)} candidate chunks")
        return selected

    def generate_summary(self, text: str, persona: str, job: str) -> str:
        # Prompt without repeating job, instruct not to include job text in summary
        prompt = (
            f"<|system|>\nYou are a {persona} assistant.\n"
            f"<|user|>\nProvide concise, actionable details based on this text. dont select headings like conclusion or introduction\n"
            f"Do not repeat or restate the job description.\nText:\n{text[:400]}\n<|assistant|>"
        )
        resp = self.llm(
            prompt,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            stop=["<|user|>", "<|system|>"],
            echo=False
        )
        summary = resp['choices'][0]['text'].strip()
        # Remove any accidental job restatements
        summary = re.sub(r'Job:.*', '', summary, flags=re.IGNORECASE).strip()
        return summary

    def _get_title(self, text: str) -> Any:
        lines = text.split('\n')[:3]
        title_pattern = re.compile(r'^[A-Z][A-Za-z0-9 \-\',\.:]+$')
        for l in lines:
            line = l.strip()
            if title_pattern.match(line) and 3 < len(line) < 80:
                return line
        return None

    def process_documents(self, pdf_files: List[str], persona: str, job: str) -> Dict:
        start_time = time.time()
        start_ts = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        print(f"[STATUS] Starting processing of {len(pdf_files)} documents at {start_ts}")
        all_chunks = []
        for f in pdf_files:
            all_chunks.extend(self.extract_text_chunks(f))
        candidates = self.rank_chunks(all_chunks, persona, job)

        extracted = []
        subsections = []
        count = 0
        for chunk in candidates:
            if time.time() - start_time > 55 or count >= self.config.max_chunks:
                break
            title = self._get_title(chunk['text'])
            if not title:
                continue
            count += 1
            print(f"[STATUS] Processing '{title}' from {chunk['document']} (page {chunk['page']})")
            summary = self.generate_summary(chunk['text'], persona, job)
            extracted.append({
                'document': chunk['document'],
                'section_title': title,
                'importance_rank': count,
                'page_number': chunk['page']
            })
            subsections.append({
                'document': chunk['document'],
                'refined_text': summary,
                'page_number': chunk['page']
            })

        total_time = time.time() - start_time
        print(f"[STATUS] Completed in {total_time:.2f}s")
        return {
            'metadata': {
                'input_documents': [Path(f).name for f in pdf_files],
                'persona': persona,
                'job_to_be_done': job,
                'processing_timestamp': time.strftime('%Y-%m-%dT%H:%M:%S.%f', time.gmtime())
            },
            'extracted_sections': extracted,
            'subsection_analysis': subsections
        }


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--persona", required=True)
    parser.add_argument("--job", required=True)
    parser.add_argument("--output", default="output/result.json")
    parser.add_argument("--model", default=None)
    args = parser.parse_args()

    config = Config(model_path=args.model or Config.model_path)
    processor = DocumentProcessor(config)

    pdfs = list(Path(args.input_dir).glob("*.pdf"))
    if not pdfs:
        print("No PDFs found in", args.input_dir)
        return

    print("[STATUS] Found PDFs:", [p.name for p in pdfs])
    result = processor.process_documents([str(p) for p in pdfs], args.persona, args.job)
    os.makedirs(Path(args.output).parent, exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[STATUS] Results saved to {args.output}")

if __name__ == '__main__':
    main()
