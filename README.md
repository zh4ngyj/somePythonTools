# Some tools
Some tools coded in Python.

## Convert all PDF files in the specified directory into one PDF file

[pdf_join.py](pdf_join.py)

core: 

~~~python
# Create catalog 
pdf_writer.add_outline_item('Catelog', 0)  # root node

# Assuming that the first page of each PDF file is the beginning of a chapter, add the chapter to the table of contents
current_page = 0

# Extract file names and remove suffixes
depart_names = get_depart_path(book_file_path)

for i, path in enumerate(paths):
    pdf_reader = PdfReader(path)
    chapter_outline = pdf_writer.add_outline_item(f'{depart_names[i]}', current_page)
    current_page += len(pdf_reader.pages)

# Write to output PDF file
with open(output, "wb") as out:
    pdf_writer.write(out)
~~~

## Audio format conversion

[audio_convert.py](audio_convert.py)

core: 

~~~python
audio = AudioSegment.from_mp3(file_name)
audio.export(target_file_name, format=target_format)
~~~