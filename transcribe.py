import speech_recognition as sr
from process_audio import * 
from os import path
from pyi18n import PyI18n

i18n = PyI18n(('en', 'ua'), load_path="translations/")
_ = i18n.gettext

lang_dict = {
	"en": "en-US",
	"ua": "uk-UA",
}

def transcribe_audio(lang: str, filename: str, mode: str):
	try:
		AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), filename)
		file_ext = get_file_ext(filename)

		if file_ext == '.mp3':
			mp3_to_wav(AUDIO_FILE)
			file_ext = ".wav"

		filepath = f"audio{'.wav' if file_ext == '.mp3' else file_ext}"
		FILE = path.join(path.dirname(path.realpath(__file__)), filepath)

		r = sr.Recognizer()
		with sr.AudioFile(FILE) as source:
			audio = r.record(source)
		try:
			transcript = r.recognize_google(audio, language=lang_dict[lang])			
			if mode == 'text':
				return f"{_(lang, 'transcription')}:\n{transcript}"
			else:
				with open('transcript.txt', 'w') as f:
					f.write(transcript)
				return transcript
		except sr.UnknownValueError:
			return _(lang, "errors.unknown_audio")
		except sr.RequestError as e:
			return f"{_(lang, 'errors.gsr_request_fail')} {e}"
	except Exception as err:
		print(err)
		return _(lang, "errors.read_fail")