import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import wikipedia
import pyjokes
import requests
import json
import re

listener = sr.Recognizer()

engine = pyttsx3.init()

voices = engine.getProperty('voices')
if len(voices) > 1:
    engine.setProperty('voice', voices[1].id)
else:
    engine.setProperty('voice', voices[0].id)
    
def talk(text):
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()


def take_command(listener, source):
    command = ""
    try:
        print("\n----- Mic ON: Listening for a command... -----")
        audio = listener.listen(
            source,
            timeout=5,
            phrase_time_limit=5
        )
        command = listener.recognize_google(
            audio,
            language="en-in"
        )
        command = command.lower()
        if "veda" in command:
            command = command.replace("veda", "").strip()
        print(f"DEBUG: Recognized command: '{command}'")
    except sr.WaitTimeoutError:
        print("No voice detected")
    except sr.UnknownValueError:
        print("Could not understand")
    except sr.RequestError:
        print("Google speech service unavailable")
    except Exception as e:
        print("Error:", e)
    return command


def extract_unity_command(command):
    text = (command or "").strip().lower()
    if not text:
        return None

    cleaned = re.sub(r"[^a-z\s]", " ", text)
    words = [word for word in cleaned.split() if word]

    if any(word in {"go", "move", "forward"} for word in words):
        return "go"
    if any(word in {"stop", "halt", "freeze"} for word in words):
        return "stop"
    return None


def run_veda(command):

    if command == "":
        return
    
    # --- DEBUG: Print the exact command being processed ---
    print(f"DEBUG: run_veda received command: '{command}'")

    # --- Unity Commands ---
    unity_command = extract_unity_command(command)
    if unity_command:
        try:
            print(f"DEBUG: Sending Unity command '{unity_command}' to Django backend...")
            # Send the command to the Django backend
            response = requests.post("http://localhost:8000/command/", json={'command': unity_command})
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            print(f"DEBUG: Successfully sent command. Backend response: {response.json()}")
            talk(f"Sending command to Unity: {unity_command}")
        except requests.exceptions.RequestException as e:
            talk(f"Could not connect to the game backend. Error: {e}")
        return
    
    elif "play" in command:
        song = command.replace("play", "").strip()

        talk("Playing " + song)
        pywhatkit.playonyt(song)


    elif "time" in command:
        time = datetime.datetime.now().strftime("%I:%M %p")

        talk("Current time is " + time)


    elif "who is" in command or "who the heck is" in command:
        person = command.replace("who is", "")
        person = person.replace("who the heck is", "")
        person = person.strip()

        try:
            info = wikipedia.summary(person, sentences=2)

            print(info)
            talk(info)

        except wikipedia.exceptions.DisambiguationError:
            talk("There are multiple results. Please be more specific.")

        except wikipedia.exceptions.PageError:
            talk("I could not find information about that.")


    elif "date" in command:
        talk("Sorry, I don't like dates.")


    elif "are you single" in command:
        talk("I am in a relationship with WiFi.")

    elif "joke" in command:
        talk(pyjokes.get_joke())

    elif "exit" in command or "quit" in command:
        talk("Goodbye")
        exit()
    elif any(greeting in command for greeting in ["hi", "hello", "hola", "hai", "hey", "howdy", "what's up"]):
            talk("Hello! what's in your mind bro?" or "Hi! How can I assist you today?" or "Hola! What can I do for you?" or "Hello! How can I help you today?" or "Hi! What can I assist you with?" or "Hola! How can I be of service to you?")
    
    else:
        talk(" I didn't get it. Please say the command again ra mawa.")


if __name__ == "__main__":

    talk("Hello, I am Veda. How can I help you?")

    try:
        with sr.Microphone(device_index=2) as source:
            print("Calibrating microphone...")
            listener.adjust_for_ambient_noise(source, duration=1)
            while True:
                command = take_command(listener, source)
                if command:
                    run_veda(command)
    except Exception as e:
        print(f"An error with the microphone occurred: {e}")
        talk("I am having trouble with my microphone. Please restart me.")