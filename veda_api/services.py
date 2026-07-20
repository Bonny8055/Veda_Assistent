import datetime
import random
import os
import hashlib

import pyjokes
import wikipedia
from gtts import gTTS
from django.conf import settings
from django.urls import reverse


class VedaAssistant:
    """Keyword-based command handler used by the Django API."""

    def _generate_audio(self, text_response: str) -> str | None:
        """
        Generates an MP3 audio file from text, saves it, and returns its URL.
        Uses a hash of the text for the filename to avoid re-generating audio.
        """
        if not text_response:
            return None

        try:
            # Use a hash of the text as the filename for caching
            text_hash = hashlib.md5(text_response.encode()).hexdigest()
            filename = f"{text_hash}.mp3"
            filepath = os.path.join(settings.MEDIA_ROOT, filename)

            # Create media directory if it doesn't exist
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

            if not os.path.exists(filepath):
                tts = gTTS(text=text_response, lang='en', slow=False)
                tts.save(filepath)

            return settings.MEDIA_URL + filename
        except Exception as e:
            print(f"Error generating audio: {e}")
            return None

    def process_command(self, command, input_type="voice"):
        command = (command or "").strip().lower()
        response_text = ""
        try:
            if any(word in command for word in ("hello", "hi", "hey", "hola")):
                response_text = random.choice(("Hello! How can I assist you today?", "Hi! What can I do for you?", "Hey! Happy to see you here!"))
            elif "who are you" in command or "your name" in command:
                response_text = "I am Veda, your intelligent voice assistant."
            elif "play" in command:
                song = command.replace("play", "", 1).strip()
                if song:
                    response_text = f"Playing {song}"
                    action, data = "play_video", song
                else:
                    response_text = "Please specify what song you would like me to play."
                    action, data = None, None
            elif "time" in command:
                response_text = f"Current time is {datetime.datetime.now().strftime('%I:%M %p')}"
            elif "date" in command:
                response_text = f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}"
            elif "who is" in command or "what is" in command:
                phrase = "who is" if "who is" in command else "what is"
                term = command.replace(phrase, "", 1).strip()
                try:
                    response_text = wikipedia.summary(term, sentences=2)
                except wikipedia.exceptions.DisambiguationError:
                    response_text = f"Multiple results found for {term}. Please be more specific."
                except wikipedia.exceptions.PageError:
                    response_text = f"Sorry, I could not find information about {term}."
                except Exception:
                    response_text = "There was an error searching Wikipedia. Please try again."
            elif "search" in command:
                term = command.replace("search", "", 1).strip()
                if term:
                    response_text = f"Searching for {term}"
                    action, data = "web_search", term
                else:
                    response_text = "Please specify what you want to search for."
                    action, data = None, None
            elif "joke" in command:
                response_text = pyjokes.get_joke()
            elif "weather" in command:
                response_text = "I cannot check weather directly yet, but I can search for current weather updates."
                action, data = "web_search", "current weather forecast"
            elif "thank" in command:
                response_text = random.choice(("You are welcome!", "Happy to help!", "Anytime!"))
            elif "how are you" in command:
                response_text = "I am functioning perfectly and ready to help."
            elif any(word in command for word in ("bye", "exit", "quit")):
                response_text = "Goodbye!"
                action, data = "exit", None
            elif "help" in command:
                response_text = "You can ask me to play a song, tell you the time, search Wikipedia, or tell you a joke."
            else:
                response_text = "I am not sure I understand. Say 'help' to see what I can do."
            
            # Default action and data if not set
            action = locals().get("action")
            data = locals().get("data")
            status = "success"

        except Exception as e:
            print(f"Error processing command '{command}': {e}")
            response_text = "Sorry, I encountered an internal error."
            action, data, status = None, None, "error"

        # Generate audio from the final response text
        audio_url = self._generate_audio(response_text)

        return {
            "text": response_text,
            "audio_url": audio_url,
            "action": action,
            "data": data,
            "input_type": input_type,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "status": status,
        }


veda = VedaAssistant()
