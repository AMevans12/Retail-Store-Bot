import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import sounddevice as sd
import wave
import threading
import whisper
from deep_translator import GoogleTranslator
import pandas as pd
import numpy as np
import google.generativeai as genai
import warnings
import grpc


warnings.filterwarnings('ignore')

#ln 18 , 123 -> Add your Gemma / Gemini API to these lines
genai.configure(api_key="")
model = genai.GenerativeModel("gemini-2.0-flash")
exit_keywords = {"quit", "bye", "exit"}
recording = False

def load_dataset(csv_path):
    return pd.read_csv(csv_path)

def process_audio(file_path):
    model = whisper.load_model("medium")
    transcription_result = model.transcribe(file_path)
    return transcription_result["text"], transcription_result["language"]

def translate_text(text, source_lang, target_lang="en"):
    return GoogleTranslator(source=source_lang, target=target_lang).translate(text) if source_lang != target_lang else text

def query_dataset(question, dataset, conversation_history):
    conversation_history.append({"role": "user", "content": question})
    
    
    dataset_summary = dataset.head(240).to_string(index=False)  

    
    prompt = f"""
    You are an AI assistant specializing in analyzing gaming products. Here is a sample of the dataset you should refer to:
    
    {dataset_summary}

    Answer user questions based on this dataset only. If the information isn't available, just say so.

    Conversation history:
    """
    for message in conversation_history:
        prompt += f"{message['role'].capitalize()}: {message['content']}\n"

    response = model.generate_content(prompt)
    response_text = response.text if response else "I couldn't find relevant data."
    
    conversation_history.append({"role": "assistant", "content": response_text})
    return response_text


def process_query():
    question = user_input.get()
    if question.lower() in exit_keywords:
        chat_display.insert(tk.END, "\nAssistant: Goodbye!\n")
        clean_exit()
        return
    dataset_response = query_dataset(question, dataset, conversation_history)
    chat_display.insert(tk.END, f"\nYou: {question}\nAssistant: {dataset_response}\n")
    user_input.delete(0, tk.END)

def record_audio():
    global recording
    recording = True
    chat_display.insert(tk.END, "\nRecording started... Speak now!\n")

    def _record():
        with wave.open("recorded_audio.wav", "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit audio (higher quality)
            wf.setframerate(44100)
            frames = []
            
            with sd.InputStream(samplerate=44100, channels=1, dtype="int16") as stream:
                while recording:
                    data, _ = stream.read(1024)
                    frames.append(data)

        
            audio_data = np.concatenate(frames, axis=0)

            # Apply simple noise reduction (mean subtraction)
            noise_level = np.mean(audio_data[:500])  # Estimate noise from first 500 samples
            cleaned_audio = audio_data - noise_level  

            # Save cleaned audio
            wf.writeframes(cleaned_audio.astype(np.int16).tobytes())

        chat_display.insert(tk.END, "\nRecording stopped. Processing...\n")
        process_audio_input("recorded_audio.wav")

    threading.Thread(target=_record).start()


def stop_recording():
    global recording
    recording = False

def process_audio_input(audio_path):
    chat_display.insert(tk.END , '\nProcessing your audio...Please wait.\n')
    root.update()
    question, detected_language = process_audio(audio_path)
    dataset_response = query_dataset(question, dataset, conversation_history)
    chat_display.insert(tk.END, f"\nYou (Audio): {question}\nAssistant: {dataset_response}\n")

def select_audio_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        process_audio_input(file_path)

def clean_exit():
    global recording
    recording = False  
    try:
        genai.configure(api_key="")  
    except Exception:
        pass

    # Properly shut down gRPC
    try:
        grpc.experimental.exit_gracefully()
    except AttributeError:
        pass  

    root.quit()

# Load dataset
dataset = load_dataset("gaming_products_data.csv")
conversation_history = []

# UI Setup
root = tk.Tk()
root.title("Gadgets Luxury AI Chatbot")
root.geometry("700x550")
root.configure(bg="#1a1a2e")  # Dark Gradient Background

whisper_languages = {
    "Afrikaans": "af",
    "Albanian": "sq",
    "Amharic": "am",
    "Arabic": "ar",
    "Armenian": "hy",
    "Assamese": "as",
    "Azerbaijani": "az",
    "Basque": "eu",
    "Belarusian": "be",
    "Bengali": "bn",
    "Bosnian": "bs",
    "Bulgarian": "bg",
    "Catalan": "ca",
    "Chinese": "zh",
    "Croatian": "hr",
    "Czech": "cs",
    "Danish": "da",
    "Dutch": "nl",
    "English": "en",
    "Estonian": "et",
    "Faroese": "fo",
    "Finnish": "fi",
    "French": "fr",
    "Galician": "gl",
    "Georgian": "ka",
    "German": "de",
    "Greek": "el",
    "Gujarati": "gu",
    "Haitian Creole": "ht",
    "Hebrew": "he",
    "Hindi": "hi",
    "Hungarian": "hu",
    "Icelandic": "is",
    "Indonesian": "id",
    "Italian": "it",
    "Japanese": "ja",
    "Javanese": "jv",
    "Kannada": "kn",
    "Kazakh": "kk",
    "Khmer": "km",
    "Korean": "ko",
    "Lao": "lo",
    "Latin": "la",
    "Latvian": "lv",
    "Lithuanian": "lt",
    "Macedonian": "mk",
    "Malay": "ms",
    "Malayalam": "ml",
    "Maltese": "mt",
    "Maori": "mi",
    "Marathi": "mr",
    "Mongolian": "mn",
    "Myanmar (Burmese)": "my",
    "Nepali": "ne",
    "Norwegian": "no",
    "Persian": "fa",
    "Polish": "pl",
    "Portuguese": "pt",
    "Punjabi": "pa",
    "Romanian": "ro",
    "Russian": "ru",
    "Sanskrit": "sa",
    "Serbian": "sr",
    "Sinhala": "si",
    "Slovak": "sk",
    "Slovenian": "sl",
    "Spanish": "es",
    "Sundanese": "su",
    "Swahili": "sw",
    "Swedish": "sv",
    "Tagalog": "tl",
    "Tamil": "ta",
    "Telugu": "te",
    "Thai": "th",
    "Turkish": "tr",
    "Ukrainian": "uk",
    "Urdu": "ur",
    "Uzbek": "uz",
    "Vietnamese": "vi",
    "Welsh": "cy",
    "Yoruba": "yo"
}


style = ttk.Style()
style.configure("TButton", font=("Arial", 12), padding=5, relief="flat", background="#00adb5", foreground="black")
style.configure("TLabel", font=("Arial", 14), background="#1a1a2e", foreground="#00adb5")
style.configure("TEntry", font=("Arial", 12), padding=5, fieldbackground="#eeeeee", foreground="black")

frame = tk.Frame(root, bg="#16213e", padx=20, pady=20)
frame.pack(pady=10, padx=10, fill="both", expand=True)

title_label = ttk.Label(frame, text="Gadgets Luxury AI Chatbot", font=("Arial", 16, "bold"), background="#16213e", foreground="#00adb5")
title_label.pack(pady=5)

chat_display = scrolledtext.ScrolledText(frame, width=80, height=20, bg="#0f3460", fg="white", font=("Arial", 12), wrap=tk.WORD)
chat_display.pack(pady=5)

user_input = ttk.Entry(frame, width=50)
user_input.pack(pady=5)

buttons_frame = tk.Frame(frame, bg="#16213e")
buttons_frame.pack(pady=5)

send_button = ttk.Button(buttons_frame, text="Send", command=process_query)
send_button.grid(row=0, column=0, padx=5)

record_button = ttk.Button(buttons_frame, text="Record Audio", command=record_audio)
record_button.grid(row=0, column=1, padx=5)

stop_button = ttk.Button(buttons_frame, text="Stop Recording", command=stop_recording)
stop_button.grid(row=0, column=2, padx=5)

select_audio_button = ttk.Button(buttons_frame, text="Select Audio File", command=select_audio_file)
select_audio_button.grid(row=0, column=3, padx=5)

root.mainloop() 