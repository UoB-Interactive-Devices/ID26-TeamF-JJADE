import speech_recognition as sr

# Initialize the recognizer
r = sr.Recognizer()

# Use the microphone as source
with sr.Microphone() as source:
    print(">>> Listening (Google)...")
    # This helps filter out background hiss
    r.adjust_for_ambient_noise(source, duration=0.5)
    audio = r.listen(source)

try:
    # recognize_google uses the free web API
    text = r.recognize_google(audio)
    print(f"Google thinks you said: {text}")
    
except sr.UnknownValueError:
    print("Google could not understand the audio.")
except sr.RequestError as e:
    print(f"Could not request results from Google; {e}")