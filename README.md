# tools
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

## Data Encryption Standard

[des.py](security/des.py)

core:

~~~python
def DES(plain, key, method):
    # 16 enc sub skc
    sub_keys = sub_key_gen(int2bin(key, 64))
    
    if method == 'decrypt':
        # 16 dec sk
        sub_keys = sub_keys[::-1]
    
    # initial permutation
    m = IP(int2bin(plain, 64))
    
    # 64-》2 group 32 bit data
    #Convert variable m to a NumPy array of integer type,
    #Then reshape this array into a two row array (the number of columns per row is automatically calculated),
    #Finally, convert this two line array into two Python lists,
    #And assign these two lists to variables l and r respectively
    l, r = np.array(m, dtype=int).reshape(2, -1).tolist()
    
    for i in range(16):
        # 16 rounds of execution: L' = R, R'= L XOR F (R, sub key)
        # L' and R' serve as L for the next iteration, R
        l, r = goRound(l, r, sub_keys[i])
    
    # binary to integer
    return bin2int(FP(r + l))
~~~