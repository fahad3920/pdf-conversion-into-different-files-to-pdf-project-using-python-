import streamlit as st
import fitz  # PyMuPDF
from fpdf import FPDF
from PIL import Image
import os
from PyPDF2 import PdfMerger
import base64
from pdf2docx import Converter
from docx2pdf import convert as docx2pdf_convert
import tempfile

# Add custom CSS for mobile responsiveness and improved layout
st.markdown("""
    <style>
    /* Make sidebar full width on small screens */
    @media (max-width: 768px) {
        .css-1d391kg {  /* Streamlit sidebar class */
            width: 100% !important;
            min-width: 100% !important;
        }
        .css-1d391kg > div {
            padding: 0 10px !important;
        }
        /* Adjust main content padding */
        .css-1d391kg ~ div {
            padding: 10px !important;
        }
    }
    /* Improve button size and spacing */
    .stButton > button {
        padding: 12px 20px;
        font-size: 16px;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

def get_file_download_link(file_path, label):
    with open(file_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    href = f'<a href="data:file/{file_path.split(".")[-1]};base64,{b64}" download="{os.path.basename(file_path)}">{label}</a>'
    return href

def convert_images_to_pdf(image_paths, output_pdf):
    pdf = FPDF()
    for img_path in image_paths:
        image = Image.open(img_path)
        pdf.add_page()
        pdf.image(img_path, 0, 0, 210, 297)  # A4 size
    pdf.output(output_pdf)
    st.success(f"Saved PDF: {output_pdf}")
    st.markdown(get_file_download_link(output_pdf, f"Download {os.path.basename(output_pdf)}"), unsafe_allow_html=True)

def convert_pdf_to_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ''
    for page in doc:
        text += page.get_text()
    output = pdf_path.replace(".pdf", "_text.txt")
    with open(output, 'w', encoding='utf-8') as f:
        f.write(text)
    st.success(f"Text saved: {output}")
    with open(output, "r", encoding='utf-8') as f:
        st.text_area("Extracted Text", f.read(), height=300)

def extract_images_from_pdf(pdf_path, output_folder):
    doc = fitz.open(pdf_path)
    os.makedirs(output_folder, exist_ok=True)
    count = 0
    images = []
    for page_index in range(len(doc)):
        for img_index, img in enumerate(doc.get_page_images(page_index)):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            img_path = f"{output_folder}/image_{page_index+1}_{img_index+1}.png"
            if pix.n < 5:  # RGB
                pix.save(img_path)
            else:  # CMYK
                pix = fitz.Pixmap(fitz.csRGB, pix)
                pix.save(img_path)
            images.append(img_path)
            count += 1
    st.success(f"Extracted {count} images to {output_folder}")
    cols = st.columns(4)
    for i, img_path in enumerate(images):
        with cols[i % 4]:
            st.image(img_path, use_column_width=True)

def merge_pdfs(pdf_list, output_file):
    merger = PdfMerger()
    for pdf in pdf_list:
        merger.append(pdf)
    merger.write(output_file)
    merger.close()
    st.success(f"Merged PDF saved: {output_file}")
    st.markdown(get_file_download_link(output_file, f"Download {os.path.basename(output_file)}"), unsafe_allow_html=True)

def convert_pdf_to_word(pdf_path, output_docx):
    cv = Converter(pdf_path)
    cv.convert(output_docx, start=0, end=None)
    cv.close()
    st.success(f"Converted to Word: {output_docx}")
    st.markdown(get_file_download_link(output_docx, f"Download {os.path.basename(output_docx)}"), unsafe_allow_html=True)

def convert_word_to_pdf(docx_path, output_pdf):
    # docx2pdf requires absolute paths and output folder
    output_folder = os.path.dirname(os.path.abspath(output_pdf))
    docx2pdf_convert(docx_path, output_folder)
    st.success(f"Converted to PDF: {output_pdf}")
    st.markdown(get_file_download_link(output_pdf, f"Download {os.path.basename(output_pdf)}"), unsafe_allow_html=True)

st.title("PDF Converter")

option = st.sidebar.radio(
    "Choose an operation",
    ("Convert images to PDF", "Convert PDF to text", "Extract images from PDF", "Merge multiple PDFs", "Convert PDF to Word", "Convert Word to PDF")
)

if option == "Convert images to PDF":
    uploaded_files = st.file_uploader("Upload images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
    output_pdf = st.text_input("Output PDF filename", "output.pdf")
    if st.button("Convert"):
        if uploaded_files and output_pdf:
            image_paths = []
            for uploaded_file in uploaded_files:
                with open(uploaded_file.name, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                image_paths.append(uploaded_file.name)
            convert_images_to_pdf(image_paths, output_pdf)
        else:
            st.error("Please upload images and specify output filename.")

elif option == "Convert PDF to text":
    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_pdf:
        with open(uploaded_pdf.name, "wb") as f:
            f.write(uploaded_pdf.getbuffer())
        if st.button("Convert"):
            convert_pdf_to_text(uploaded_pdf.name)

elif option == "Extract images from PDF":
    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
    output_folder = st.text_input("Output folder name", "extracted_images")
    if uploaded_pdf and output_folder:
        with open(uploaded_pdf.name, "wb") as f:
            f.write(uploaded_pdf.getbuffer())
        if st.button("Extract"):
            extract_images_from_pdf(uploaded_pdf.name, output_folder)

elif option == "Merge multiple PDFs":
    uploaded_pdfs = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True)
    output_pdf = st.text_input("Output PDF filename", "merged.pdf")
    if uploaded_pdfs and output_pdf:
        pdf_list = []
        for uploaded_pdf in uploaded_pdfs:
            with open(uploaded_pdf.name, "wb") as f:
                f.write(uploaded_pdf.getbuffer())
            pdf_list.append(uploaded_pdf.name)
        if st.button("Merge"):
            merge_pdfs(pdf_list, output_pdf)

elif option == "Convert PDF to Word":
    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
    output_docx = st.text_input("Output Word filename", "output.docx")
    if uploaded_pdf and output_docx:
        with open(uploaded_pdf.name, "wb") as f:
            f.write(uploaded_pdf.getbuffer())
        if st.button("Convert"):
            convert_pdf_to_word(uploaded_pdf.name, output_docx)

elif option == "Convert Word to PDF":
    uploaded_docx = st.file_uploader("Upload Word Document", type=["docx"])
    output_pdf = st.text_input("Output PDF filename", "output.pdf")
    if uploaded_docx and output_pdf:
        with open(uploaded_docx.name, "wb") as f:
            f.write(uploaded_docx.getbuffer())
        if st.button("Convert"):
            convert_word_to_pdf(uploaded_docx.name, output_pdf)
