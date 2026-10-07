import pytest
from unittest.mock import patch, MagicMock
import os
from extractor import ChangeOrderExtractor

@patch('extractor.os.path.exists')
@patch('instructor.from_openai')
@patch('fitz.open')
def test_empty_pdf_fallback(mock_fitz, mock_instructor, mock_exists):
    mock_exists.return_value = True
    mock_doc = MagicMock()
    mock_page = MagicMock()
    mock_page.get_text.return_value = "   " # empty text
    mock_page.get_pixmap.return_value.tobytes.return_value = b"fake_image_data"
    mock_doc.__iter__.return_value = [mock_page]
    mock_doc.__len__.return_value = 1
    mock_fitz.return_value = mock_doc
    
    ex = ChangeOrderExtractor(api_key="fake")
    
    mock_client = MagicMock()
    from tests.test_schema import make_co
    mock_co = make_co()
    mock_client.chat.completions.create.return_value = mock_co
    ex.client = mock_client
    
    res = ex.extract_from_file("fake.pdf")
    assert any("Vision fallback" in r for r in res.review_reasons)

def test_txt_handling(tmp_path):
    p = tmp_path / "test.txt"
    p.write_text("dummy text")
    ex = ChangeOrderExtractor(api_key="fake")
    
    mock_client = MagicMock()
    ex.client = mock_client
    
    with patch('extractor.compute_confidence') as mock_conf:
        mock_res = MagicMock()
        mock_res.review_reasons = []
        mock_conf.return_value = mock_res
        ex.extract_from_file(str(p))
        mock_conf.assert_called_once()
        assert mock_conf.call_args[1]['source_text'] == "dummy text"
