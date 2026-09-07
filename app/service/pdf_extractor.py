import io
import re

from pydantic import HttpUrl, TypeAdapter, ValidationError
from pypdf import PdfReader
from pypdf.errors import PyPdfError

from app.core.concurrency import run_in_threadpool
from app.core.logger import get_logger

logger = get_logger(__name__)

URL_REGEX = re.compile(r"https?://[^\s<>\"'{}|\\^`\[\]]+", re.IGNORECASE)
_http_url_adapter = TypeAdapter(HttpUrl)


def _clean_and_normalize_url(raw_url: str) -> str | None:
    """Clean trailing punctuation and normalize to canonical URL form."""
    cleaned = raw_url.strip()
    cleaned = re.sub(r"[.,;:!?\)]+$", "", cleaned)
    if not cleaned.startswith(("http://", "https://")):
        return None
    try:
        # Standardizes canonical form (e.g. trailing slashes on domain roots)
        return str(_http_url_adapter.validate_python(cleaned))
    except (ValidationError, ValueError):
        return None


def extract_urls_from_pdf_sync(pdf_bytes: bytes) -> list[str]:
    """Synchronously extract unique URLs from a PDF's plain text and hyperlink annotations.

    Raises:
        ValueError: If the byte string is not a valid or readable PDF.
    """
    if not pdf_bytes or not pdf_bytes.startswith(b"%PDF-"):
        raise ValueError("Invalid PDF file: Missing %PDF- header.")

    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
    except Exception as exc:
        logger.warning(f"Failed to parse PDF bytes: {exc}")
        raise ValueError(f"Corrupted or unreadable PDF: {exc}") from exc

    raw_urls: list[str] = []

    for page_idx, page in enumerate(reader.pages):
        # 1. Extract plain text URLs
        try:
            text = page.extract_text() or ""
            found_in_text = URL_REGEX.findall(text)
            for raw_u in found_in_text:
                normalized = _clean_and_normalize_url(raw_u)
                if normalized:
                    raw_urls.append(normalized)
        except (
            PyPdfError,
            KeyError,
            IndexError,
            TypeError,
            ValueError,
            AttributeError,
        ) as exc:
            logger.warning(f"Error extracting text from page {page_idx}: {exc}")

        # 2. Extract /Annots URI links
        try:
            annots = page.get("/Annots")
            if annots:
                for annot in annots:
                    annot_obj = (
                        annot.get_object() if hasattr(annot, "get_object") else annot
                    )
                    if isinstance(annot_obj, dict):
                        action = annot_obj.get("/A")
                        if action:
                            action_obj = (
                                action.get_object()
                                if hasattr(action, "get_object")
                                else action
                            )
                            if isinstance(action_obj, dict) and "/URI" in action_obj:
                                uri = str(action_obj["/URI"])
                                normalized = _clean_and_normalize_url(uri)
                                if normalized:
                                    raw_urls.append(normalized)
        except (
            PyPdfError,
            KeyError,
            IndexError,
            TypeError,
            ValueError,
            AttributeError,
        ) as exc:
            logger.warning(f"Error extracting annotations from page {page_idx}: {exc}")

    # Deduplicate preserving original document order
    seen: set[str] = set()
    unique_urls: list[str] = []
    for u in raw_urls:
        if u not in seen:
            seen.add(u)
            unique_urls.append(u)

    return unique_urls


async def extract_urls_from_pdf(pdf_bytes: bytes) -> list[str]:
    """Extract URLs from PDF bytes concurrently using the application's thread pool."""
    return await run_in_threadpool(extract_urls_from_pdf_sync, pdf_bytes)
