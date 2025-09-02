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

## Down Video by YT URL
下载youtube的视频和字幕，并且能够在没有中文简体字幕时选择自动翻译
.[download_yt_video.py](download_yt_video.py)
1. python环境
~~~bash
pip install pytube
~~~
2. 安装 ffmpeg
3. 装浏览器扩展（自动获取cookie不生效时使用）:
   1. 请为您的浏览器 (Edge, Chrome, 或 Firefox) 安装一个名为 "Get cookies.txt LOCALLY" 的扩展程序。这是一个安全的开源工具。https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc
   2. 您可以在浏览器的扩展商店中搜索并安装它。导出Cookie文件:在浏览器中登录您的YouTube账号。点击浏览器工具栏上 "Get cookies.txt LOCALLY" 扩展的图标。
   3. 在弹出的窗口中，点击 "Export" 按钮。浏览器会自动下载一个名为 cookies.txt 的文件。
   4. 放置Cookie文件:将下载的 cookies.txt 文件重命名为 youtube_cookies.txt。将这个 youtube_cookies.txt 文件移动到您的项目根目录，也就是 youtubedownloader 文件夹下。
   5. 当被问及是否使用浏览器Cookie时，可以选择“否”（n），因为脚本会自动使用您手动放置的文件
4. 执行脚本
5. 使用MKVToolNix进行视频和中文字幕手动合并
6. TODO:支持 ffmpeg 自动合并