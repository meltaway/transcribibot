from dotenv import dotenv_values
from pyi18n import PyI18n
import logging
import os
from telegram import Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler
from process_audio import * 
from process_video import *
from transcribe import *

config = dotenv_values(".env")

lang = 'en'
pfilter = 0
mode = 'text'

i18n = PyI18n(('en', 'ua'), load_path="translations/")
_ = i18n.gettext

logging.basicConfig(
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
	level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await context.bot.send_message(chat_id=update.effective_chat.id, text=_(lang, 'greeting'))

async def lang_change_en(update: Update, context: ContextTypes.DEFAULT_TYPE):
	global lang 
	lang = 'en'
	await context.bot.send_message(chat_id=update.effective_chat.id, text=_(lang, "lang_change"))

async def lang_change_ua(update: Update, context: ContextTypes.DEFAULT_TYPE):
	global lang 
	lang = 'ua'
	await context.bot.send_message(chat_id=update.effective_chat.id, text=_(lang, "lang_change"))

async def pfilter_change(update: Update, context: ContextTypes.DEFAULT_TYPE):
	if len(context.args) == 0:
		await context.bot.send_message(chat_id=update.effective_chat.id, text=_(lang, "errors.pfilter_no_value"))
	else:
		if int(context.args[0]) == 0 or int(context.args[0]) == 1:
			global pfilter 
			pfilter = int(context.args[0])
			await context.bot.send_message(chat_id=update.effective_chat.id, text=_(lang, "pfilter_change", pfilter_value=context.args[0]))
		else:
			await context.bot.send_message(chat_id=update.effective_chat.id, text=_(lang, "errors.pfilter_wrong_value"))

async def mode_text_change(update: Update, context: ContextTypes.DEFAULT_TYPE):
	global mode 
	mode = 'text'
	await context.bot.send_message(chat_id=update.effective_chat.id, text=_(lang, "mode_text_change"))

async def mode_file_change(update: Update, context: ContextTypes.DEFAULT_TYPE):
	global mode 
	mode = 'file'
	await context.bot.send_message(chat_id=update.effective_chat.id, text=_(lang, "mode_file_change"))

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await context.bot.send_message(chat_id=update.effective_chat.id, text=_(lang, "errors.unknown_command"))

async def unsupported_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
	await context.bot.send_message(chat_id=update.effective_chat.id, text=_(lang, "errors.unsupported_file"))

async def process_audio_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
	if update.message.audio:
		file_ext = get_file_ext(update.message.audio.file_name)
		if check_valid_extension(file_ext):
			try:
				await context.bot.send_message(chat_id=update.effective_chat.id, text=_(lang, "processing"))
				file = await context.bot.get_file(file_id=update.message.audio.file_id)
				with open(f"./audio{file_ext}", 'wb') as f:
					await file.download(out=f)

				transcript = transcribe_audio(lang, f"audio{file_ext}", mode)

				if mode == "text":
					await context.bot.send_message(chat_id=update.effective_chat.id, text=transcript)
				else:
					document = open("transcript.txt", "rb")
					await context.bot.send_document(chat_id=update.effective_chat.id, document=document)

				if os.path.exists(f"audio{file_ext}"):
					os.remove(f"audio{file_ext}")

				if os.path.exists("transcript.txt"):
					os.remove("transcript.txt")
			except:
				await context.bot.send_message(chat_id=update.effective_chat.id, text=_(lang, "errors.read_fail"))
		else:
			await context.bot.send_message(chat_id=update.effective_chat.id, text=_(lang, "errors.audio_ext_fail"))
	else:
		await context.bot.send_message(chat_id=update.effective_chat.id, text=_(lang, "errors.audio_ext_fail"))

async def process_video_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
	if update.message.document:
		file_ext = get_file_ext(update.message.document.file_name)
		try:
			await context.bot.send_message(chat_id=update.effective_chat.id, text=_(lang, "processing"))
			file = await context.bot.get_file(file_id=update.message.document.file_id)
			with open(f"./video{file_ext}", 'wb') as f:
				await file.download(out=f)

			convert_video_to_audio(f"./video{file_ext}")
			transcript = transcribe_audio(lang, "audio.wav", mode)
			await context.bot.send_message(chat_id=update.effective_chat.id, text=transcript)

			if os.path.exists("audio.wav"):
				os.remove("audio.wav")
		except:
			await context.bot.send_message(chat_id=update.effective_chat.id, text=_(lang, "errors.read_fail"))
	else:
		await context.bot.send_message(chat_id=update.effective_chat.id, text=_(lang, "errors.video_ext_fail"))

if __name__ == "__main__":
	application = ApplicationBuilder().token(config["API_TOKEN"]).build()
	
	start_handler = CommandHandler('start', start)
	lang_change_en_handler = CommandHandler('en', lang_change_en)
	lang_change_ua_handler = CommandHandler('ua', lang_change_ua)
	pfilter_change_handler = CommandHandler('profanity', pfilter_change)
	mode_text_change_handler = CommandHandler('mode_text', mode_text_change)
	mode_file_change_handler = CommandHandler('mode_file', mode_file_change)
	audio_file_handler = MessageHandler(filters.VOICE | filters.AUDIO | filters.Document.MP3 | filters.Document.WAV, process_audio_file)
	video_file_handler = MessageHandler(filters.VIDEO_NOTE | filters.VIDEO | filters.Document.MP4, process_video_file)
	unsupported_file_handler = MessageHandler((~filters.VOICE) | (~filters.AUDIO) | (~filters.Document.MP3) | (~filters.Document.WAV) | (~filters.VIDEO_NOTE) | (~filters.VIDEO) | (~filters.Document.MP4), unsupported_file)
	unknown_handler = MessageHandler(filters.COMMAND | filters.TEXT, unknown_command)
	
	application.add_handler(start_handler)
	application.add_handler(lang_change_en_handler)
	application.add_handler(lang_change_ua_handler)
	application.add_handler(pfilter_change_handler)
	application.add_handler(mode_text_change_handler)
	application.add_handler(mode_file_change_handler)
	application.add_handler(audio_file_handler)
	application.add_handler(video_file_handler)
	application.add_handler(unknown_handler)
	
	application.run_polling()