from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List

import requests
from bs4 import BeautifulSoup


@dataclass
class ScrapeResult:
    url: str
    title: str
    summary: str
    key_entities: dict
    sections: List[str]
    raw_text: str


def fetch_article(url: str, timeout: int = 15) -> ScrapeResult:
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    title_tag = soup.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else "Untitled Article"

    paragraphs = soup.select("#mw-content-text p")
    summary_parts = []
    for p in paragraphs:
        text = p.get_text(strip=True)
        if text:
            summary_parts.append(text)
        if len(" ".join(summary_parts)) > 500:
            break
    summary = " ".join(summary_parts)[:1200]

    # Extract section headings (h2/h3)
    sections = []
    for header in soup.select("#mw-content-text h2, #mw-content-text h3"):
        section_title = header.get_text(" ", strip=True)
        if section_title:
            cleaned = re.sub(r"\[.*?\]", "", section_title).strip()
            if cleaned and cleaned not in sections:
                sections.append(cleaned)

    raw_text = soup.get_text(" ", strip=True)

    # Naive entity extraction based on capitalization; limited but lightweight
    words = re.findall(r"\b[A-Z][a-zA-Z]+\b", raw_text)
    people = []
    organizations = []
    locations = []
    for w in words:
        if w.lower() in {"the", "a", "an", "and"}:
            continue
        if w not in people:
            people.append(w)
    # Simple buckets; real entity extraction would use NLP libraries
    key_entities = {
        "people": people[:10],
        "organizations": organizations,
        "locations": locations,
    }

    return ScrapeResult(
        url=url,
        title=title,
        summary=summary,
        key_entities=key_entities,
        sections=sections,
        raw_text=raw_text,
    )
