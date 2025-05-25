import os
import pytest
from main import convert_images_to_pdf, convert_pdf_to_text, extract_images_from_pdf, merge_pdfs
from PIL import Image

@pytest.fixture
def sample_images(tmp_path):
    img1 = tmp_path / "img1.png"
    img2 = tmp_path / "img2.png"
    image = Image.new('RGB', (100, 100), color = 'red')
    image.save(img1)
    image = Image.new('RGB', (100, 100), color = 'blue')
    image.save(img2)
    return [str(img1), str(img2)]

@pytest.fixture
def sample_pdf(tmp_path):
    # Create a simple PDF with fpdf for testing
    from fpdf import FPDF
    pdf_path = tmp_path / "test.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Hello World", ln=1, align='C')
    pdf.output(str(pdf_path))
    return str(pdf_path)

def test_convert_images_to_pdf(sample_images, tmp_path):
    output_pdf = tmp_path / "output.pdf"
    convert_images_to_pdf(sample_images, str(output_pdf))
    assert os.path.exists(output_pdf)
    assert os.path.getsize(output_pdf) > 0

def test_convert_pdf_to_text(sample_pdf, tmp_path):
    convert_pdf_to_text(sample_pdf)
    output_txt = sample_pdf.replace(".pdf", "_text.txt")
    assert os.path.exists(output_txt)
    with open(output_txt, 'r', encoding='utf-8') as f:
        content = f.read()
    assert "Hello World" in content

def test_extract_images_from_pdf(sample_pdf, tmp_path):
    output_folder = tmp_path / "images"
    extract_images_from_pdf(sample_pdf, str(output_folder))
    # Since the sample PDF has no images, folder may be empty but should exist
    assert os.path.exists(output_folder)

def test_merge_pdfs(sample_pdf, tmp_path):
    output_pdf = tmp_path / "merged.pdf"
    merge_pdfs([sample_pdf, sample_pdf], str(output_pdf))
    assert os.path.exists(output_pdf)
    assert os.path.getsize(output_pdf) > 0
