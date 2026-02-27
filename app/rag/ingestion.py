from __future__ import annotations
from typing import List, Dict, Any
from uuid import uuid4
import io
from .utils import clean_whitespace, chunk_text
from .config import settings
import logging

logger = logging.getLogger("app.rag.ingestion")


def _load_pdf_bytes(data: bytes) -> str:
    try:
        from pypdf import PdfReader  # lazy import to avoid startup crash if optional dependency missing
    except ModuleNotFoundError as exc:
        raise RuntimeError("pypdf is required to ingest PDF files. Install with `pip install pypdf`.") from exc
    reader = PdfReader(io.BytesIO(data))
    texts: list[str] = []
    for i, page in enumerate(reader.pages):
        try:
            page_text = page.extract_text() or ""
            # mark page boundary so ingestion can track page_number
            texts.append(f"\n\n===PAGE:{i+1}===\n\n" + page_text)
        except Exception as exc:
            logger.exception("Error extracting PDF page: %s", exc)
    return "\n".join(texts)


def _load_txt_bytes(data: bytes) -> str:
    return data.decode("utf-8", errors="ignore")


def ingest_file_bytes(filename: str, data: bytes) -> List[Dict[str, Any]]:
    text = ""
    if filename.lower().endswith(".pdf"):
        text = _load_pdf_bytes(data)
    else:
        text = _load_txt_bytes(data)
    text = clean_whitespace(text)
    # Enhanced section-aware chunking:
    import re
    chunks = []
    # split by page markers inserted earlier
    pages = re.split(r"\n===PAGE:(\d+)===", text)
    # pages list will be like ['', '1', 'page1text', '2', 'page2text', ...] or similar
    i = 0
    page_iter = []
    if len(pages) > 1:
        # reconstruct (page_num, page_text)
        it = iter(pages)
        first = next(it, "")
        while True:
            num = next(it, None)
            if num is None:
                break
            body = next(it, "")
            page_iter.append((int(num), body))
    else:
        page_iter.append((1, text))

    heading_re = re.compile(r"^\s*(\d+(?:\.\d+)*)\s+(.+)$")
    allcaps_re = re.compile(r"^[A-Z0-9 ,\-\(\)\/]{4,}$")
    for page_num, page_text in page_iter:
        # split lines to detect headings
        lines = page_text.split("\n")
        current_section_title = ""
        current_section_number = ""
        section_buffer = []
        def flush_section(buf, sec_title, sec_num, pg_num):
            joined = "\n".join(buf).strip()
            if not joined:
                return []
            out = []
            for idx, ch in enumerate(chunk_text(joined, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)):
                ch_clean = clean_whitespace(ch)
                if not ch_clean:
                    continue
                chunk_id = str(uuid4())
                metadata = {"source": filename, "section_title": sec_title, "section_number": sec_num, "page_number": pg_num, "chunk_index": idx}
                out.append({"id": chunk_id, "text": ch_clean, "metadata": metadata})
            return out

        for ln in lines:
            ln_stripped = ln.strip()
            if not ln_stripped:
                # blank line — keep accumulating
                section_buffer.append(ln)
                continue
            m = heading_re.match(ln_stripped)
            if m:
                # flush previous
                chunks.extend(flush_section(section_buffer, current_section_title, current_section_number, page_num))
                section_buffer = []
                current_section_number = m.group(1)
                current_section_title = m.group(2)
                continue
            if allcaps_re.match(ln_stripped) and len(ln_stripped.split()) <= 6:
                # treat as heading
                chunks.extend(flush_section(section_buffer, current_section_title, current_section_number, page_num))
                section_buffer = []
                current_section_title = ln_stripped
                current_section_number = ""
                continue
            # normal line
            section_buffer.append(ln)
        # flush remaining buffer for the page
        chunks.extend(flush_section(section_buffer, current_section_title, current_section_number, page_num))
    # Deduplicate by text
    seen = set()
    deduped = []
    for c in chunks:
        if c["text"] in seen:
            continue
        seen.add(c["text"])
        deduped.append(c)
    logger.info("Ingested %d chunks from %s", len(deduped), filename)
    return deduped

