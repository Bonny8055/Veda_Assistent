import datetime
import random

try:
    import pyjokes
except ImportError:  # pragma: no cover
    pyjokes = None

try:
    import wikipedia
except ImportError:  # pragma: no cover
    wikipedia = None

try:
    import pywhatkit
except ImportError:  # pragma: no cover
    pywhatkit = None

try:
    import pyttsx3
except ImportError:  # pragma: no cover
    pyttsx3 = None


class VoiceAssistant:
    def __init__(self):
        self.engine = None
        if pyttsx3 is not None:
            try:
                self.engine = pyttsx3.init()
                voices = self.engine.getProperty('voices')
                if voices:
                    if len(voices) > 1:
                        self.engine.setProperty('voice', voices[1].id)
                    else:
                        self.engine.setProperty('voice', voices[0].id)
            except Exception:
                self.engine = None

    def talk(self, text):
        if self.engine is not None:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception:
                pass
        return text

    def handle_command(self, command):
        text = (command or "").strip().lower()
        if not text:
            return "Please enter a command first."

        if "play" in text:
            song = text.replace("play", "").strip()
            if pywhatkit is not None:
                try:
                    pywhatkit.playonyt(song)
                except Exception as exc:
                    return f"I could not play that song right now. {exc}"
            return f"Playing {song or 'your requested song'}"

        if "time" in text:
            time_value = datetime.datetime.now().strftime("%I:%M %p")
            return f"The current time is {time_value}."

        if "who is" in text or "who the heck is" in text:
            person = text.replace("who is", "").replace("who the heck is", "").strip()
            if wikipedia is not None:
                try:
                    info = wikipedia.summary(person, sentences=2)
                    return info
                except wikipedia.exceptions.DisambiguationError:
                    return "There are multiple results. Please be more specific."
                except wikipedia.exceptions.PageError:
                    return "I could not find information about that."
            return f"I can search for {person} if Wikipedia is available."

        if "date" in text:
            return "Sorry, I do not like dates."

        if "are you single" in text:
            return "I am in a relationship with Wi-Fi."

        

        if "joke" in text:
            if pyjokes is not None:
                try:
                    return pyjokes.get_joke()
                except Exception:
                    return "I could not think of a joke right now."
            return "A joke is available when the joke library is installed."

        if "stop" in text or "exit" in text or "quit" in text:
            return "Goodbye! dengai"
        
        greetings = ["hi", "hello", "hola", "hai", "hey", "howdy", "what's up"]
        if any(greeting in text for greeting in greetings):
            responses = [
                "Hello! What's on your mind, bro?",
                "Hi! How can I assist you today?",
                "Hola! What can I do for you?",
                "Hello! How can I help you today?",
                "Hi! What can I assist you with?",
                "Hola! How can I be of service to you?"
            ]
            return random.choice(responses)


        return " I didnt get it."


assistant = VoiceAssistant()


def process_command(command, speak=False):
    response = assistant.handle_command(command)
    if speak:
        assistant.talk(response)
    return response
