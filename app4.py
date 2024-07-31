
import os
import random
import speech_recognition as sr
import openai
import pyttsx3
import tkinter as tk
from PIL import Image, ImageTk
import cv2
from gtts import gTTS
import pygame
import tempfile


OPENAI_API_KEY = 'api_key'

openai.api_key = OPENAI_API_KEY

r = sr.Recognizer()

engine = pyttsx3.init()

voices = engine.getProperty('voices')
voice_map = {
    'en': 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_DAVID_11.0',  # English (US)
    'fr': 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_FR-FR_HORTENSE_11.0',  # French
    'ar': 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_AR-SA_HODA_11.0'  # Arabic
}
language_voice = {
    'en': None,
    'fr': None,
    'ar': None
}

for voice in voices:
    for lang, voice_id in voice_map.items():
        if voice.id == voice_id:
            language_voice[lang] = voice.id

language_codes = {
    'en': 'en-US',
    'fr': 'fr-FR',
    'ar': 'ar-EG'
}

def recognise_speech():
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            print("Start listening")
            audio = r.listen(source)
            print("End speech")

            recognized_text = ""
            detected_language = ""
            for lang, lang_code in language_codes.items():
                try:
                    recognized_text = r.recognize_google(audio, language=lang_code).lower()
                    if recognized_text:
                        detected_language = lang
                        break
                except sr.UnknownValueError:
                    continue

    except sr.RequestError as e:
        print(f"Could not request results; {e}")

    return recognized_text, detected_language

def get_error_response(language):
    error_responses = {
        "en": [
            "Excuse me, could you rephrase that?",
            "I apologize, I missed that. Could you repeat it, please?",
            "Would you mind repeating what you just said?",
            "I didn't catch what you said, do you mind repeating what you said?",
            "Sorry, there might be some background noise. Could you repeat that?",
            "Is it just me, or did something cut out? Mind saying that again?",
            "I'm not quite sure I understood. Could you repeat please?"
        ],
        "fr": [
            "Excusez-moi, pourriez-vous reformuler cela ?",
            "Je m'excuse, j'ai raté ça. Pourriez-vous répéter, s'il vous plaît ?",
            "Pourriez-vous répéter ce que vous venez de dire ?",
            "Je n'ai pas compris ce que vous avez dit, pouvez-vous répéter ?",
            "Désolé, il y a peut-être du bruit de fond. Pourriez-vous répéter ?",
            "Est-ce juste moi, ou quelque chose s'est coupé ? Pouvez-vous répéter ?",
            "Je ne suis pas sûr d'avoir compris. Pouvez-vous répéter s'il vous plaît ?"
        ],
        "ar": [
            "عذرًا، هل يمكن أن تعيد صياغة ذلك؟",
            "أعتذر، لقد فاتني ذلك. هل يمكنك تكراره، من فضلك؟",
            "هل تمانع في تكرار ما قلته للتو؟",
            "لم أفهم ما قلته، هل يمكنك التكرار؟",
            "آسف، قد يكون هناك ضوضاء في الخلفية. هل يمكنك التكرار؟",
            "هل هو فقط أنا، أم أن هناك شيئًا انقطع؟ هل تمانع في إعادة قول ذلك؟",
            "لست متأكدًا من أنني فهمت. هل يمكنك التكرار من فضلك؟"
        ]
    }
    return random.choice(error_responses[language])

def update_background(cap, video_label):
    ret, frame = cap.read()
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = Image.fromarray(frame)
        frame = frame.resize((video_label.winfo_width(), video_label.winfo_height()), Image.LANCZOS)
        frame_image = ImageTk.PhotoImage(frame)
        video_label.config(image=frame_image)
        video_label.image = frame_image
    video_label.after(50, update_background, cap, video_label)

def chat():
    recognized_text, lang = recognise_speech()
    print("Recognised speech:", recognized_text)
    answer = ""

    if not recognized_text:
        answer = get_error_response(lang if lang else 'en')
    else:
        question_prompt = (
            "You are BrainTrain, an enthusiastic and knowledgeable assistant. "
            "You love learning all about robots and sharing that knowledge with curious minds. "
            "Please provide a direct and accurate answer to the following question: "
        )
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question_prompt + recognized_text}
            ]
        )
        answer = response['choices'][0]['message']['content'].strip()

    print("Answer: ", answer)
    response_label.config(text=answer)
    text_to_speech(answer, lang)
    return answer

def text_to_speech(text, lang):
    if lang == 'ar':
        pass
        # Use gTTS for Arabic
        tts = gTTS(text=text, lang='ar')
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            tts.save(fp.name)
            fp_path = fp.name
        pygame.mixer.init()
        pygame.mixer.music.load(fp_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.quit()
        os.remove(fp_path)
    else:
        # Use pyttsx3 for other languages
        if lang in language_voice and language_voice[lang]:
            selected_voice = language_voice[lang]
            print(f"Selected voice for {lang}: {selected_voice}")

            engine.setProperty('voice', selected_voice)
            engine.say(text)
            engine.runAndWait()
        else:
            print(f"No voice found for {lang}")



root = tk.Tk()
root.title("Brain Train")
root.geometry("800x600")

cap1 = cv2.VideoCapture('pulse.gif')

video_label1 = tk.Label(root)
video_label1.pack(padx=3, pady=3, side=tk.TOP, fill=tk.BOTH, expand=True)

response_label = tk.Label(root, text="", font=("Helvetica", 16))
response_label.pack(padx=3, pady=3, side=tk.BOTTOM, fill=tk.X, expand=True)

speak_button = tk.Button(root, text="start", command=chat, font=("Helvetica", 16), bg="black", fg="blue")
speak_button.place(relx=0.5, rely=0.95, anchor=tk.CENTER)

update_background(cap1, video_label1)

root.mainloop()

cap1.release()
