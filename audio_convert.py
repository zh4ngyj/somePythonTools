# pip install pydub
from pydub import AudioSegment

def audio_convert(file_name, target_file_name, target_format):
    audio = AudioSegment.from_mp3(file_name)
    audio.export(target_file_name, format=target_format)

if __name__ == "__main__":
    file_name = "abc.mp3"
    target_file_name = "abc.wav"
    target_format = "wav"
    audio_convert(file_name, target_file_name, target_format)
