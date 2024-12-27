# pip install PyPDF2
# pip install reportlab

import os
from PyPDF2 import PdfReader, PdfWriter

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

book_page_number = 1
book_file_path = r"E:\MIT-Linear-Algebra-Notes-master"
book_merge_name = 'MIT线性代数.pdf'

def create_page_number_overlay(page_number):
    # 创建一个PDF页面，用于存放页码
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    # 设置页码位置
    can.setFont("Helvetica", 12)
    can.drawString(550, 20, f"Page {page_number}")  # 假设使用Letter尺寸，页码放在右下角
    can.save()
    packet.seek(0)
    return PdfReader(packet)


def merge_pdfs(paths, output):
    
    global book_page_number
    
    pdf_writer = PdfWriter()

    for path in paths:
        pdf_reader = PdfReader(path)
        for page_number in range(len(pdf_reader.pages)):
            # # 将每一页添加到PdfFileWriter对象中
            # pdf_writer.add_page(pdf_reader.pages[page_number])
            
            # 获取当前页
            page = pdf_reader.pages[page_number]
            # 创建页码水印
            overlay = create_page_number_overlay(book_page_number)
            book_page_number = book_page_number + 1
            # 将页码水印添加到页面上
            page.merge_page(overlay.pages[0])
            # 将带有页码的页面添加到PdfFileWriter对象中
            pdf_writer.add_page(page)
    
    # 创建目录
    pdf_writer.add_outline_item('目录', 0)  # 目录的根节点

    # 假设每个PDF文件的第一页是章节的开始，添加章节到目录
    current_page = 0
    
    # 提取文件名并去除后缀
    depart_names = get_depart_path(book_file_path)
    
    for i, path in enumerate(paths):
        pdf_reader = PdfReader(path)
        chapter_outline = pdf_writer.add_outline_item(f'{depart_names[i]}', current_page)
        current_page += len(pdf_reader.pages)

    # 写入到输出PDF文件
    with open(output, "wb") as out:
        pdf_writer.write(out)


def find_all_pdf_path(folder_path=str):

    # 递归便利文件夹，找到所有的PDF文件，并获取它们的绝对路径
    pdf_files = [
        os.path.join(root, file)
        for root, dirs, files in os.walk(folder_path)
        for file in files
        if file.lower().endswith(".pdf")
    ]
    return pdf_files


def merged_pdf(folder_path=str):
    
    # 调用函数查询目录下的全部PDF文件路径列表
    pdf_paths = find_all_pdf_path(folder_path=folder_path)

    # 合并后的文件的名称
    output_pdf = book_merge_name

    # 调用函数合并PDF
    merge_pdfs(pdf_paths, output_pdf)
    
def get_depart_path(folder_path=str):
    items = []
    for item in os.listdir(folder_path):
        full_path = os.path.join(folder_path, item)
        if os.path.isdir(full_path):
            items.append(item)
    return items

if __name__ == "__main__":
    
    # 合并
    merged_pdf(folder_path=book_file_path)
    
