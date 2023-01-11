import moviepy.editor as mp

def convert_video_to_audio(filename: str):
	clip = mp.VideoFileClip(filename)
	clip.audio.write_audiofile("audio.wav")