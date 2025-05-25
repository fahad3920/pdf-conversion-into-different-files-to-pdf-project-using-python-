import fitz  # PyMuPDF
from fpdf import FPDF
from PIL import Image
import os
from PyPDF2 import PdfMerger

def convert_images_to_pdf(image_paths, output_pdf):
    pdf = FPDF()
    for img_path in image_paths:
        image = Image.open(img_path)
        width, height = image.size
        pdf.add_page()
        pdf.image(img_path, 0, 0, 210, 297)  # A4 size
    pdf.output(output_pdf)
    print(f"Saved PDF: {output_pdf}")

def convert_pdf_to_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ''
    for page in doc:
        text += page.get_text()
    output = pdf_path.replace(".pdf", "_text.txt")
    with open(output, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"Text saved: {output}")

def extract_images_from_pdf(pdf_path, output_folder):
    doc = fitz.open(pdf_path)
    os.makedirs(output_folder, exist_ok=True)
    count = 0
    for page_index in range(len(doc)):
        for img_index, img in enumerate(doc.get_page_images(page_index)):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            if pix.n < 5:  # RGB
                pix.save(f"{output_folder}/image_{page_index+1}_{img_index+1}.png")
            else:  # CMYK
                pix = fitz.Pixmap(fitz.csRGB, pix)
                pix.save(f"{output_folder}/image_{page_index+1}_{img_index+1}.png")
            count += 1
    print(f"Extracted {count} images to {output_folder}")

def merge_pdfs(pdf_list, output_file):
    merger = PdfMerger()
    for pdf in pdf_list:
        merger.append(pdf)
    merger.write(output_file)
    merger.close()
    print(f"Merged PDF saved: {output_file}")

import subprocess
import sys
import threading

def run_cli():
    print("Running CLI interface...")
    print("PDF Converter Menu")
    print("1. Convert images to PDF")
    print("2. Convert PDF to text")
    print("3. Extract images from PDF")
    print("4. Merge multiple PDFs")
    choice = input("Enter your choice: ")

    if choice == '1':
        images = input("Enter image paths separated by commas: ").split(",")
        output = input("Enter output PDF filename: ")
        convert_images_to_pdf(images, output)
    elif choice == '2':
        pdf = input("Enter PDF filename: ")
        convert_pdf_to_text(pdf)
    elif choice == '3':
        pdf = input("Enter PDF filename: ")
        folder = input("Enter output folder name: ")
        extract_images_from_pdf(pdf, folder)
    elif choice == '4':
        pdfs = input("Enter PDF filenames separated by commas: ").split(",")
        output = input("Enter output PDF filename: ")
        merge_pdfs(pdfs, output)
    else:
        print("Invalid choice.")

def run_streamlit():
    print("Launching Streamlit web interface...")
    subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app.py"])

if __name__ == "__main__":
    cli_thread = threading.Thread(target=run_cli)
    streamlit_thread = threading.Thread(target=run_streamlit)

    cli_thread.start()
    streamlit_thread.start()

    cli_thread.join()
    streamlit_thread.join()
