# pip install PyPDF2
# pip install reportlab
import os
from PyPDF2 import PdfReader, PdfWriter

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

book_page_number = 1
book_file_path = r"E:\your_file_path"
book_merge_name = 'abc.pdf'

def create_page_number_overlay(page_number):
    # Create a PDF page to store page numbers
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    # Set page position
    can.setFont("Helvetica", 12)
    can.drawString(550, 20, f"Page {page_number}")  # Assuming Letter size is used, the page numbers are placed in the bottom right corner
    can.save()
    packet.seek(0)
    return PdfReader(packet)


def merge_pdfs(paths, output):
    
    global book_page_number
    
    pdf_writer = PdfWriter()

    for path in paths:
        pdf_reader = PdfReader(path)
        for page_number in range(len(pdf_reader.pages)):
            # # Add each page to the PdfFileWriter object
            # pdf_writer.add_page(pdf_reader.pages[page_number])
            
            # Get the current page
            page = pdf_reader.pages[page_number]
            # Create page number watermark
            overlay = create_page_number_overlay(book_page_number)
            book_page_number = book_page_number + 1
            # Add page number watermark to the page
            page.merge_page(overlay.pages[0])
            # Add pages with page numbers to the PdfFileWriter object
            pdf_writer.add_page(page)
    
    # Create catalog 
    pdf_writer.add_outline_item('Catalog', 0)  # root node

    # Assuming that the first page of each PDF file is the beginning of a chapter, add the chapter to the table of contents
    current_page = 0
    
    # Extract file names and remove suffixes
    depart_names = get_depart_path(book_file_path)
    
    for i, path in enumerate(paths):
        pdf_reader = PdfReader(path)
        chapter_outline = pdf_writer.add_outline_item(f'{depart_names[i]}', current_page)
        current_page += len(pdf_reader.pages)

    # Write to PDF
    with open(output, "wb") as out:
        pdf_writer.write(out)


def find_all_pdf_path(folder_path=str):

    # Recursive convenience folder, find all PDF files and obtain their absolute paths
    pdf_files = [
        os.path.join(root, file)
        for root, dirs, files in os.walk(folder_path)
        for file in files
        if file.lower().endswith(".pdf")
    ]
    return pdf_files


def merged_pdf(folder_path=str):
    
    # Call the function to query the list of all PDF file paths in the directory
    pdf_paths = find_all_pdf_path(folder_path=folder_path)

    # The name of the merged file
    output_pdf = book_merge_name

    # Call a function to merge PDFs
    merge_pdfs(pdf_paths, output_pdf)
    
def get_depart_path(folder_path=str):
    items = []
    for item in os.listdir(folder_path):
        full_path = os.path.join(folder_path, item)
        if os.path.isdir(full_path):
            items.append(item)
    return items

if __name__ == "__main__":
    
    # Merge
    merged_pdf(folder_path=book_file_path)
    
