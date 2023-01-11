from pydub import AudioSegment
import pathlib

FILE_EXTS = ['.mp3', '.wav', '.aiff', '.flac']

def get_file_ext(filename: str):
	suffixes = pathlib.Path(filename).suffixes
	return suffixes[-1]

def check_valid_extension(ext: str):
	if ext in FILE_EXTS:
		return True
	else:
		return False

def mp3_to_wav(file: str):
	sound = AudioSegment.from_mp3(file)
	sound.export('audio.wav', format="wav")