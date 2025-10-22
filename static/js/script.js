// static/js/script.js
class VedaAssistant {
    constructor() {
        this.isListening = false;
        this.recognition = null;
        this.initializeSpeechRecognition();
        this.loadCommandHistory();
        this.setupEventListeners();
    }

    initializeSpeechRecognition() {
        if ('webkitSpeechRecognition' in window) {
            this.recognition = new webkitSpeechRecognition();
        } else if ('SpeechRecognition' in window) {
            this.recognition = new SpeechRecognition();
        } else {
            this.showError('Speech recognition not supported in this browser.');
            return;
        }

        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.lang = 'en-US';

        this.recognition.onstart = () => {
            this.isListening = true;
            this.updateVoiceUI(true);
        };

        this.recognition.onresult = (event) => {
            const command = event.results[0][0].transcript;
            this.processCommand(command, 'voice');
        };

        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.showError(`Voice recognition error: ${event.error}`);
            this.updateVoiceUI(false);
        };

        this.recognition.onend = () => {
            this.updateVoiceUI(false);
        };
    }

    setupEventListeners() {
        // Text input enter key
        document.getElementById('textInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendTextCommand();
            }
        });

        // Voice button
        document.getElementById('startBtn').addEventListener('click', () => {
            this.toggleVoiceRecognition();
        });

        // Clear history
        document.getElementById('clearHistoryBtn').addEventListener('click', () => {
            this.clearHistory();
        });

        // Load history on page load
        window.addEventListener('load', () => {
            this.loadCommandHistory();
        });
    }

    toggleVoiceRecognition() {
        if (!this.recognition) {
            this.showError('Speech recognition not available.');
            return;
        }

        if (this.isListening) {
            this.recognition.stop();
        } else {
            this.recognition.start();
        }
    }

    updateVoiceUI(listening) {
        const startBtn = document.getElementById('startBtn');
        const voiceStatus = document.getElementById('voiceStatus');

        if (listening) {
            startBtn.classList.add('listening');
            startBtn.innerHTML = '🎤<div class="typing-indicator"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div>';
            voiceStatus.textContent = 'Listening... Speak now!';
            voiceStatus.style.color = '#ef4444';
        } else {
            startBtn.classList.remove('listening');
            startBtn.innerHTML = '🎤';
            voiceStatus.textContent = 'Click microphone to speak';
            voiceStatus.style.color = '';
        }
    }

    sendTextCommand() {
        const textInput = document.getElementById('textInput');
        const command = textInput.value.trim();
        
        if (command) {
            this.processCommand(command, 'text');
            textInput.value = '';
        } else {
            this.showError('Please enter a command first!');
        }
    }

    processCommand(command, inputType) {
        this.showThinking();
        
        fetch('/process-command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                command: command,
                input_type: inputType 
            })
        })
        .then(response => response.json())
        .then(data => {
            this.displayResponse(data, command, inputType);
            this.loadCommandHistory();
        })
        .catch(error => {
            console.error('Error:', error);
            this.showError('Failed to process command. Please try again.');
        });
    }

    showThinking() {
        const responseDiv = document.getElementById('response');
        responseDiv.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px;">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
                <span>Veda is thinking...</span>
            </div>
        `;
    }

    displayResponse(data, originalCommand, inputType) {
        const responseDiv = document.getElementById('response');
        let actionHTML = '';
        
        if (data.action === 'play_video') {
            actionHTML = `
                <div style="margin-top: 15px;">
                    <button class="btn btn-accent" onclick="window.open('https://www.youtube.com/results?search_query=${encodeURIComponent(data.data)}', '_blank')">
                        🎵 Watch "${data.data}" on YouTube
                    </button>
                </div>
            `;
        } else if (data.action === 'web_search') {
            actionHTML = `
                <div style="margin-top: 15px;">
                    <button class="btn btn-secondary" onclick="window.open('https://www.google.com/search?q=${encodeURIComponent(data.data)}', '_blank')">
                        🔍 Search for "${data.data}"
                    </button>
                </div>
            `;
        }

        responseDiv.innerHTML = `
            <div style="margin-bottom: 15px; padding: 12px; background: white; border-radius: 8px;">
                <strong>You (${inputType}):</strong> "${originalCommand}"
                <span class="input-type-badge">${inputType}</span>
            </div>
            <div style="padding: 12px;">
                <strong>Veda:</strong> ${data.text}
                ${actionHTML}
            </div>
        `;

        this.speakText(data.text);
    }

    speakText(text) {
        if ('speechSynthesis' in window) {
            const cleanText = text.replace(/[🤖🎵🕐📅📚😂🔍💬🧮⛅❓🎲❌🤔👋😊🌟🚀🌈💫💪🤗😄]/g, '')
                                .replace(/\*\*(.*?)\*\*/g, '$1');
            
            const utterance = new SpeechSynthesisUtterance(cleanText);
            utterance.rate = 0.9;
            utterance.pitch = 1.2;  // Higher pitch for female voice
            utterance.volume = 0.8;
            
            // Get available voices and select a female voice
            const voices = speechSynthesis.getVoices();
            const femaleVoice = voices.find(voice => 
                voice.name.includes('Female') || 
                voice.name.includes('female') ||
                voice.name.includes('Google UK English Female') ||
                voice.name.includes('Microsoft Zira') ||
                voice.name.includes('Samantha') ||
                voice.lang.includes('en-US') && voice.name.toLowerCase().includes('female')
            );
            
            if (femaleVoice) {
                utterance.voice = femaleVoice;
            } else {
                // Fallback: use any available English voice
                const englishVoice = voices.find(voice => voice.lang.includes('en'));
                if (englishVoice) {
                    utterance.voice = englishVoice;
                }
            }
            
            speechSynthesis.speak(utterance);
        }
    }
//////////////////////////////////////////////////////////////////////////////////////
    setSuggestion(text) {
        document.getElementById('textInput').value = text;
        document.getElementById('textInput').focus();
    }

    loadCommandHistory() {
        fetch('/command-history')
            .then(response => response.json())
            .then(data => {
                this.displayHistory(data.history || []);
            })
            .catch(error => {
                console.error('Error loading history:', error);
            });
    }

    displayHistory(history) {
        const historyContainer = document.getElementById('historyContainer');
        
        if (history.length === 0) {
            historyContainer.innerHTML = `
                <div style="text-align: center; padding: 40px; color: var(--text-light);">
                    <div style="font-size: 48px; margin-bottom: 16px;">📝</div>
                    <p>No commands yet. Start chatting with Veda!</p>
                </div>
            `;
            return;
        }

        // Reverse to show latest first
        const reversedHistory = [...history].reverse();
        
        historyContainer.innerHTML = reversedHistory.map(item => `
            <div class="history-item">
                <div class="history-command">
                    ${item.Command}
                    <span class="input-type-badge">${item.InputType}</span>
                </div>
                <div class="history-response">${item.Response}</div>
                <div style="font-size: 12px; color: var(--text-light); margin-top: 8px;">
                    ${new Date(item.Timestamp).toLocaleString()}
                </div>
            </div>
        `).join('');
    }

    clearHistory() {
        if (confirm('Are you sure you want to clear all command history?')) {
            fetch('/clear-history', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    this.loadCommandHistory();
                    this.showMessage('History cleared successfully!');
                } else {
                    this.showError('Failed to clear history.');
                }
            })
            .catch(error => {
                console.error('Error clearing history:', error);
                this.showError('Failed to clear history.');
            });
        }
    }

    showError(message) {
        this.showMessage(message, 'error');
    }

    showMessage(message, type = 'info') {
        // Create toast notification
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 16px 24px;
            background: ${type === 'error' ? '#ef4444' : '#10b981'};
            color: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;
        
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => document.body.removeChild(toast), 300);
        }, 3000);
    }
}

// Initialize the assistant when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.veda = new VedaAssistant();
});

// Add CSS for toast animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);