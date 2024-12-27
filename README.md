# tools
Some tools coded in Python.

## Convert all PDF files in the specified directory into one PDF file

[pdf_join.py](pdf_join.py)

example: 

~~~python
merged_pdf(folder_path='your_file_root_path')
~~~

## Audio format conversion

[audio_convert.py](audio_convert.py)

example: 

~~~python
audio = AudioSegment.from_mp3(file_name)
audio.export(target_file_name, format=target_format)
~~~