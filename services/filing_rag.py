from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Iterable


_WORD_RE = re.compile(r"\b[a-zA-Z]{3,}\b")


@dataclass
class RetrievalChunk:
    year: int
    text: str
    overlap: int


def _load_filing_texts(ticker: str, years: Iterable[int] | None, filings_dir: str) -> dict[int, str]:
    base_dir = os.path.join(filings_dir, ticker.upper())
    if not os.path.exists(base_dir):
        return {}

    requested = set(years) if years else None
    texts: dict[int, str] = {}

    for name in sorted(os.listdir(base_dir)):
        if not name.endswith(".txt"):
            continue
        try:
            year = int(name.replace(".txt", ""))
        except ValueError:
            continue

        if requested is not None and year not in requested:
            continue

        path = os.path.join(base_dir, name)
        with open(path, "r", encoding="utf-8") as handle:
            texts[year] = handle.read()

    return texts


def _tokenize(text: str) -> set[str]:
    return set(_WORD_RE.findall(text.lower()))


def _split_sentences(text: str, max_chars: int = 360) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks: list[str] = []

    for sent in sentences:
        sent = sent.strip()
        if not sent:
            continue
        if len(sent) <= max_chars:
            chunks.append(sent)
        else:
            chunks.append(sent[:max_chars])

    return chunks


def retrieve_relevant_chunks(
    ticker: str,
    question: str,
    years: Iterable[int] | None = None,
    filings_dir: str = "data/sec",
    top_k: int = 5,
) -> list[RetrievalChunk]:
    texts = _load_filing_texts(ticker=ticker, years=years, filings_dir=filings_dir)
    if not texts:
        return []

    query_tokens = _tokenize(question)
    candidates: list[RetrievalChunk] = []

    for year, filing_text in texts.items():
        for chunk in _split_sentences(filing_text):
            overlap = len(_tokenize(chunk).intersection(query_tokens))
            if overlap > 0:
                candidates.append(RetrievalChunk(year=year, text=chunk, overlap=overlap))

    candidates.sort(key=lambda c: (c.overlap, c.year), reverse=True)
    return candidates[:top_k]


def answer_question_over_filings(
    ticker: str,
    question: str,
    years: Iterable[int] | None = None,
    filings_dir: str = "data/sec",
    top_k: int = 5,
) -> dict:
    """Retrieval-first QA over local filing text with optional OpenAI synthesis."""
    chunks = retrieve_relevant_chunks(
        ticker=ticker,
        question=question,
        years=years,
        filings_dir=filings_dir,
        top_k=top_k,
    )

    if not chunks:
        return {
            "ticker": ticker.upper(),
            "question": question,
            "answer": "No relevant filing evidence was found in local data/sec text files.",
            "citations": [],
        }

    highlights = []
    citations = []

    for idx, chunk in enumerate(chunks, start=1):
        highlights.append(f"[{idx}] ({chunk.year}) {chunk.text}")
        citations.append({"index": idx, "year": chunk.year, "snippet": chunk.text})

    answer = _generate_answer(ticker=ticker, question=question, highlights=highlights)

    return {
        "ticker": ticker.upper(),
        "question": question,
        "answer": answer,
        "citations": citations,
    }


def _generate_answer(ticker: str, question: str, highlights: list[str]) -> str:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key or api_key == "your_openai_key_here":
        return _fallback_answer(ticker=ticker, highlights=highlights)

    try:
        from langchain_openai import ChatOpenAI

        model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        llm = ChatOpenAI(model=model_name, temperature=0.1, api_key=api_key)
        evidence = "\n".join(highlights)
        prompt = (
            "You are a financial filings analyst.\n"
            f"Ticker: {ticker.upper()}\n"
            f"Question: {question}\n"
            "Use only the evidence below and cite snippets as [n].\n"
            "If evidence is weak, say so clearly. Keep it concise.\n\n"
            f"Evidence:\n{evidence}"
        )
        response = llm.invoke(prompt)
        content = getattr(response, "content", "")
        if isinstance(content, list):
            content = " ".join([str(part) for part in content])
        text = str(content).strip()
        return text or _fallback_answer(ticker=ticker, highlights=highlights)
    except Exception:
        return _fallback_answer(ticker=ticker, highlights=highlights)


def _fallback_answer(ticker: str, highlights: list[str]) -> str:
    return (
        f"Based on retrieved filing evidence for {ticker.upper()}, the strongest signals are:\n"
        + "\n".join(highlights)
    )
