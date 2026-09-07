"""Test cases for PDF bookmark upload endpoint."""

from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import pypdf
import pytest
from httpx import AsyncClient

SAMPLE_PDF_PATH = Path("tests/data/sample_urls.pdf")
SAME_PDF_PATH = Path("tests/data/same_urls.pdf")


@pytest.fixture(scope="module")
def sample_pdf_bytes() -> bytes:
    """Fixture providing raw bytes of sample_urls.pdf."""
    return SAMPLE_PDF_PATH.read_bytes()


@pytest.fixture(scope="module")
def same_pdf_bytes() -> bytes:
    """Fixture providing raw bytes of same_urls.pdf."""
    return SAME_PDF_PATH.read_bytes()


class TestUploadPdfBookmarks:
    """Test POST /bookmarks/upload-pdf endpoint."""

    @pytest.mark.asyncio
    async def test_upload_pdf_all_new_urls(
        self, client_with_auth: AsyncClient, sample_pdf_bytes: bytes
    ):
        """Upload sample PDF when no bookmarks exist yet."""
        files = {"file": ("sample_urls.pdf", sample_pdf_bytes, "application/pdf")}
        response = await client_with_auth.post("/bookmarks/upload-pdf", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "All bookmarks created successfully"
        assert data["total_found"] == 4
        assert data["created_count"] == 4
        assert data["existing_count"] == 0
        assert len(data["bookmarks"]) == 4

        urls = [b["original_url"] for b in data["bookmarks"]]
        assert any("fastapi.tiangolo.com" in u for u in urls)
        assert any("docs.python.org" in u for u in urls)
        assert any("bookmark-shortner" in u for u in urls)
        assert any("sqlalchemy.org" in u for u in urls)

    @pytest.mark.asyncio
    async def test_upload_pdf_with_existing_urls(
        self, client_with_auth: AsyncClient, sample_pdf_bytes: bytes
    ):
        """When some URLs already exist, reuse their short codes and return the expected message."""
        # 1. Pre-create one bookmark
        pre_created = await client_with_auth.post(
            "/bookmarks/", json={"original_url": "https://fastapi.tiangolo.com"}
        )
        assert pre_created.status_code == 200
        existing_bm = pre_created.json()
        existing_short_code = existing_bm["short_code"]
        existing_id = existing_bm["id"]

        # 2. Upload sample PDF containing this URL plus 3 new ones
        files = {"file": ("sample_urls.pdf", sample_pdf_bytes, "application/pdf")}
        response = await client_with_auth.post("/bookmarks/upload-pdf", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Some of them already exist"
        assert data["total_found"] == 4
        assert data["created_count"] == 3
        assert data["existing_count"] == 1
        assert len(data["bookmarks"]) == 4

        # Verify the pre-existing bookmark preserved its original short_code and id
        matched = [
            b for b in data["bookmarks"] if "fastapi.tiangolo.com" in b["original_url"]
        ]
        assert len(matched) == 1
        assert matched[0]["short_code"] == existing_short_code
        assert matched[0]["id"] == existing_id

    @pytest.mark.asyncio
    async def test_upload_pdf_repeat_all_exist(
        self, client_with_auth: AsyncClient, sample_pdf_bytes: bytes
    ):
        """When all URLs in the PDF already exist, return existing shortcodes and duplicate message."""
        files = {"file": ("sample_urls.pdf", sample_pdf_bytes, "application/pdf")}
        # First upload
        resp1 = await client_with_auth.post("/bookmarks/upload-pdf", files=files)
        assert resp1.status_code == 200
        data1 = resp1.json()

        # Second upload of the same file
        files2 = {"file": ("sample_urls.pdf", sample_pdf_bytes, "application/pdf")}
        resp2 = await client_with_auth.post("/bookmarks/upload-pdf", files=files2)
        assert resp2.status_code == 200
        data2 = resp2.json()

        assert data2["message"] == "Some of them already exist"
        assert data2["total_found"] == 4
        assert data2["created_count"] == 0
        assert data2["existing_count"] == 4

        codes1 = {b["original_url"]: b["short_code"] for b in data1["bookmarks"]}
        codes2 = {b["original_url"]: b["short_code"] for b in data2["bookmarks"]}
        assert codes1 == codes2

    @pytest.mark.asyncio
    async def test_upload_pdf_with_internal_duplicate_same_urls(
        self, client_with_auth: AsyncClient, same_pdf_bytes: bytes
    ):
        """Upload a PDF containing repeated occurrences of the same URLs."""
        files = {"file": ("same_urls.pdf", same_pdf_bytes, "application/pdf")}
        resp = await client_with_auth.post("/bookmarks/upload-pdf", files=files)
        assert resp.status_code == 200
        data = resp.json()

        # The 8 link occurrences in the document collapse to 4 unique URLs
        assert data["total_found"] == 4
        assert len(data["bookmarks"]) == 4

        # Uploading the same PDF again should trigger duplicate detection
        files2 = {"file": ("same_urls.pdf", same_pdf_bytes, "application/pdf")}
        resp2 = await client_with_auth.post("/bookmarks/upload-pdf", files=files2)
        assert resp2.status_code == 200
        data2 = resp2.json()

        assert data2["message"] == "Some of them already exist"
        assert data2["total_found"] == 4
        assert data2["created_count"] == 0
        assert data2["existing_count"] == 4

    @pytest.mark.asyncio
    async def test_upload_pdf_without_auth(
        self, client: AsyncClient, sample_pdf_bytes: bytes
    ):
        """Unauthenticated user cannot upload PDF."""
        files = {"file": ("sample_urls.pdf", sample_pdf_bytes, "application/pdf")}
        response = await client.post("/bookmarks/upload-pdf", files=files)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_upload_non_pdf_file(self, client_with_auth: AsyncClient):
        """Reject files with non-pdf extensions."""
        files = {"file": ("urls.txt", b"https://example.com", "text/plain")}
        response = await client_with_auth.post("/bookmarks/upload-pdf", files=files)
        assert response.status_code == 400
        assert "must be a PDF" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_upload_empty_pdf(self, client_with_auth: AsyncClient):
        """Reject empty PDF files."""
        files = {"file": ("empty.pdf", b"", "application/pdf")}
        response = await client_with_auth.post("/bookmarks/upload-pdf", files=files)
        assert response.status_code == 400
        assert "empty" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_upload_corrupted_pdf(self, client_with_auth: AsyncClient):
        """Reject corrupted PDF content."""
        files = {"file": ("corrupt.pdf", b"%PDF-invalid-bytes-xyz", "application/pdf")}
        response = await client_with_auth.post("/bookmarks/upload-pdf", files=files)
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_upload_pdf_no_urls_found(self, client_with_auth: AsyncClient):
        """Reject PDF files that contain no URLs."""
        writer = pypdf.PdfWriter()
        writer.add_blank_page(width=200, height=200)
        bio = BytesIO()
        writer.write(bio)

        files = {"file": ("blank.pdf", bio.getvalue(), "application/pdf")}
        response = await client_with_auth.post("/bookmarks/upload-pdf", files=files)
        assert response.status_code == 400
        assert "No URLs found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_upload_pdf_uses_concurrency_threadpool(
        self, client_with_auth: AsyncClient, sample_pdf_bytes: bytes
    ):
        """Verify that PDF URL extraction executes via run_in_threadpool."""
        with patch(
            "app.service.pdf_extractor.run_in_threadpool",
            wraps=__import__(
                "app.core.concurrency", fromlist=["run_in_threadpool"]
            ).run_in_threadpool,
        ) as spy_pool:
            files = {"file": ("sample_urls.pdf", sample_pdf_bytes, "application/pdf")}
            response = await client_with_auth.post("/bookmarks/upload-pdf", files=files)
            assert response.status_code == 200
            assert spy_pool.call_count >= 1
