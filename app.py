# app.py
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import datetime
import wikipedia
import pyjokes
import pandas as pd
import pywhatkit
import random
import os
import json

app = Flask(__name__)
CORS(app)

class VedaWebAssistant:
    def __init__(self):
        self.command_history = []
    
    def process_command(self, command, input_type="voice"):
        """Process commands from both voice and text input"""
        command = command.lower()
        response = {
            "text": "", 
            "action": None, 
            "data": None,
            "input_type": input_type,
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "success"
        }
        
        print(f"Processing {input_type} command: {command}")
        
        try:
            # Greeting commands
            if any(word in command for word in ['hello', 'hi', 'hey', 'hola']):
                s = ('Bro', 'buddy', 'dood', 'friend', 'pal')
                a = random.choice(s)
                responses = [
                    f"Hello {a}! How can I assist you today?",
                    f"Hi {a}! What can I do for you?",
                    f"Hey {a}! happy to see you here!"
                ]
                response["text"] = random.choice(responses)
                
            elif 'play' in command:
                song = command.replace('play', '').strip()
                if song:
                   song = command.replace('play', '')
                   response('playing ' + song)
                   pywhatkit.playonyt(song)
                else:
                    response["text"] = "Please specify what song you'd like me to play"
                    
            elif 'time' in command:
                time = datetime.datetime.now().strftime('%I:%M %p')
                response["text"] = f'🕐 Current time is {time}'
                
            elif 'date' in command:
                date = datetime.datetime.now().strftime('%A, %B %d, %Y')
                response["text"] = f"📅 Today is {date}"
                
            elif 'who is' in command:
                search_term = command.replace('who is', '').strip()
                try:
                    info = wikipedia.summary(search_term, sentences=2)
                    response["text"] = f"📚 {info}"
                except wikipedia.exceptions.DisambiguationError as e:
                    response["text"] = f"Multiple results found for {search_term}. Please be more specific."
                except wikipedia.exceptions.PageError:
                    response["text"] = f"❌ Sorry, I couldn't find information about {search_term}"
                except Exception as e:
                    response["text"] = "There was an error searching Wikipedia. Please try again."
                    
            elif 'who are you' in command:
                search_term = command.replace('I am', '').strip()
                try:
                    info = wikipedia.summary(search_term, sentences=2)
                    response["text"] = f"📚 {info}"
                except wikipedia.exceptions.DisambiguationError as e:
                    response["text"] = f"Multiple results found for {search_term}. Please be more specific."
                except wikipedia.exceptions.PageError:
                    response["text"] = f"❌ Sorry, I couldn't find information about {search_term}"
                except Exception as e:
                    response["text"] = "There was an error. Please try differently."  


            elif 'what is' in command:
                search_term = command.replace('what is', '').strip()
                try:
                    info = wikipedia.summary(search_term, sentences=2)
                    response["text"] = f"📖 {info}"
                except:
                    response["text"] = f"❌ I couldn't find a clear definition for {search_term}"
                    
            elif 'search' in command:
                search_term = command.replace('search', '').strip()
                if search_term:
                    response["text"] = f"🔍 Searching for {search_term}"
                    response["action"] = "web_search"
                    response["data"] = search_term
                else:
                    response["text"] = "Please specify what you want to search for"

            elif 'random' in command or 'how am i' in command:
                s = ('good', 'bad', 'worst', 'awesome', 'fantastic', 'amazing')
                a = random.choice(s)
                response["text"] = f"🎲 You are having a {a} day!"
                
            elif 'joke' in command:
                try:
                    joke = pyjokes.get_joke()
                    response["text"] = f"😂 {joke}"
                except:
                    response["text"] = "❓ Why don't scientists trust atoms? Because they make up everything!"
                
            elif 'your name' in command or 'who are you' in command:
                response["text"] = '🤖 I am Veda, your intelligent voice and text assistant!'
                
            elif 'weather' in command:
                response["text"] = "⛅ I can't check weather directly yet, but I can search for current weather updates!"
                response["action"] = "web_search"
                response["data"] = "current weather forecast"
                
            elif 'calculate' in command or 'math' in command:
                response["text"] = "🧮 I'm still learning math calculations. For now, try asking me to search for a calculator online!"
                
            elif 'thank' in command:
                responses = [
                    "You're welcome! 😊",
                    "Happy to help! 🌟",
                    "Anytime! 💫",
                    "Glad I could assist you! 🚀"
                ]
                response["text"] = random.choice(responses)
                
            elif 'how are you' in command:
                moods = [
                    "I'm functioning perfectly! 💪",
                    "I'm great! Ready to help you with anything. 🤗",
                    "Doing well, thanks for asking! 😄",
                    "I'm just ones and zeros, but feeling fantastic! 🌈"
                ]
                response["text"] = random.choice(moods)
                
            elif 'bye' in command or 'exit' in command or 'quit' in command:
                responses = [
                    "Goodbye! Feel free to come back if you need more assistance! 👋",
                    "See you later! It was great helping you! 😊",
                    "Bye! Don't hesitate to return if you have more questions! 🌟"
                ]
                response["text"] = random.choice(responses)
                response["action"] = "exit"
                
            elif 'help' in command:
                help_text = """
                🤖 **Here's what I can do:**
                
                **🎵 Music:** "Play [song name]"
                **🕐 Time:** "What time is it?"
                **📅 Date:** "What's today's date?"
                **📚 Knowledge:** "Who is [person]" or "What is [thing]"
                **😂 Entertainment:** "Tell me a joke"
                **🔍 Search:** "Search [anything]"
                **💬 Chat:** "How are you?", "Thank you", "Hello"
                
                Try any of these commands using text or voice!
                """
                response["text"] = help_text
                
            else:
                response["text"] = "🤔 I'm not sure I understand. Try saying 'help' to see what I can do, or ask me to play music, tell time, search Wikipedia, or tell a joke!"
            
        except Exception as e:
            response["text"] = "❌ Sorry, I encountered an error processing your command. Please try again."
            response["status"] = "error"
        
        # Log command to Excel
        self._log_command(command, response["text"], input_type)
        
        return response
    
    def _log_command(self, command, response, input_type):
        """Log commands and responses to Excel"""
        try:
            # Create data directory if it doesn't exist
            os.makedirs('data', exist_ok=True)
            file_path = 'data/commands.xlsx'
            
            try:
                df = pd.read_excel(file_path)
            except FileNotFoundError:
                df = pd.DataFrame(columns=['Command', 'Response', 'InputType', 'Timestamp'])
            
            new_entry = {
                'Command': command,
                'Response': response,
                'InputType': input_type,
                'Timestamp': datetime.datetime.now()
            }
            
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            df.to_excel(file_path, index=False)
            
        except Exception as e:
            print(f"Error logging command: {e}")

# Initialize the assistant
veda = VedaWebAssistant()

@app.route('/')
def home():
    """Serve the main interface"""
    return render_template('index.html')

@app.route('/process-command', methods=['POST'])
def process_command():
    """API endpoint to process both voice and text commands"""
    try:
        data = request.json
        command = data.get('command', '')
        input_type = data.get('input_type', 'voice')
        
        if not command:
            return jsonify({"error": "No command provided", "status": "error"}), 400
        
        response = veda.process_command(command, input_type)
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500

@app.route('/command-history', methods=['GET'])
def get_command_history():
    """Get command history from Excel file"""
    try:
        df = pd.read_excel('data/commands.xlsx')
        history = df.to_dict('records')
        # Convert Timestamp to string for JSON serialization
        for item in history:
            if isinstance(item.get('Timestamp'), datetime.datetime):
                item['Timestamp'] = item['Timestamp'].isoformat()
        return jsonify({"history": history[-10:]})  # Last 10 commands
    except FileNotFoundError:
        return jsonify({"history": []})

@app.route('/clear-history', methods=['POST'])
def clear_history():
    """Clear command history"""
    try:
        file_path = 'data/commands.xlsx'
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({"message": "History cleared successfully", "status": "success"})
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "Veda is running smoothly", 
        "timestamp": datetime.datetime.now().isoformat(),
        "version": "2.0",
        "features": ["voice_commands", "text_commands", "youtube_play", "wikipedia_search", "jokes", "web_search"]
    })

if __name__ == '__main__':
    # Create data directory
    os.makedirs('data', exist_ok=True)
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)