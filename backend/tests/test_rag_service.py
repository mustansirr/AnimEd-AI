
import pytest
from app.services.rag_service import chunk_text, _clean_text

def test_clean_text():
    text = "  This   is  a   test.  \n\n\n  New line.  "
    cleaned = _clean_text(text)
    assert cleaned == "This is a test.\n\nNew line."

def test_chunk_text_simple():
    text = "Hello world. This is a test."
    chunks = chunk_text(text, chunk_size=20, overlap=0)
    # "Hello world. This is" (20 chars) -> split
    # Should respect sentence boundaries if possible, but strict size limits apply first?
    # Our logic: 
    # start=0, end=20. search window for break.
    # "Hello world. This is" -> rfind('.') -> pos 11.
    # end becomes 11+2 = 13 ("Hello world. ")
    assert len(chunks) >= 1
    assert "Hello world." in chunks[0]

def test_chunk_text_overlap():
    text = "Sentence one. Sentence two. Sentence three."
    # chunk size enough for one sentence approx
    chunks = chunk_text(text, chunk_size=15, overlap=5)
    assert len(chunks) > 1

def test_chunk_text_empty():
    assert chunk_text("") == []
    assert chunk_text("   ") == []
