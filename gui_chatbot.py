import customtkinter as ctk
from openai import OpenAI
import os
from dotenv import load_dotenv
from pathlib import Path
import pygame
import json
from datetime import datetime

class CyberNinjaGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Initialize OpenAI and audio
        load_dotenv()
        self.client = OpenAI()
        self.setup_audio_directory()
        pygame.mixer.init()
        
        # Load or create personality settings
        self.personality_file = Path(__file__).parent / "personality.json"
        self.load_personality()
        
        # Configure window
        self.title("Cyber Ninja AI Assistant")
        self.geometry("800x600")
        
        # Configure grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Create sidebar frame
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)
        
        # Personality settings in sidebar
        self.logo_label = ctk.CTkLabel(self.sidebar, text="Personality Settings", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Voice selection
        self.voice_label = ctk.CTkLabel(self.sidebar, text="Voice:")
        self.voice_label.grid(row=1, column=0, padx=20, pady=(10, 0))
        self.voice_option = ctk.CTkOptionMenu(self.sidebar, values=["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
                                            command=self.change_voice)
        self.voice_option.grid(row=2, column=0, padx=20, pady=(0, 10))
        self.voice_option.set(self.personality["voice"])
        
        # Personality sliders
        self.create_personality_slider("Formality", "formality", 3)
        self.create_personality_slider("Tech Level", "tech_level", 5)
        self.create_personality_slider("Humor", "humor", 7)
        
        # Save personality button
        self.save_button = ctk.CTkButton(self.sidebar, text="Save Personality", command=self.save_personality)
        self.save_button.grid(row=9, column=0, padx=20, pady=10)
        
        # Create main chat frame
        self.chat_frame = ctk.CTkFrame(self)
        self.chat_frame.grid(row=0, column=1, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.chat_frame.grid_rowconfigure(0, weight=1)
        self.chat_frame.grid_columnconfigure(0, weight=1)
        
        # Create chat display
        self.chat_display = ctk.CTkTextbox(self.chat_frame, width=400, height=300)
        self.chat_display.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="nsew")
        self.chat_display.configure(state="disabled")
        
        # Create input frame
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=1, column=1, padx=(20, 20), pady=(20, 20), sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)
        
        # Create chat input
        self.chat_input = ctk.CTkEntry(self.input_frame, placeholder_text="Type your message here...")
        self.chat_input.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="ew")
        self.chat_input.bind("<Return>", self.send_message)
        
        # Create send button
        self.send_button = ctk.CTkButton(self.input_frame, text="Send", width=100, command=self.send_message)
        self.send_button.grid(row=0, column=1, padx=(10, 20), pady=20)
        
        # Audio player frame
        self.player_frame = ctk.CTkFrame(self.input_frame)
        self.player_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")
        
        # Audio controls
        self.play_button = ctk.CTkButton(self.player_frame, text="▶", width=40, command=self.toggle_audio)
        self.play_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.stop_button = ctk.CTkButton(self.player_frame, text="⏹", width=40, command=self.stop_audio)
        self.stop_button.grid(row=0, column=1, padx=5, pady=5)
        
        # Initialize state
        self.current_audio = None
        self.is_playing = False
        
        # Welcome message
        self.append_message("Cyber Ninja AI: Welcome, user. I am your cyber ninja assistant. How may I assist you today?")
    
    def setup_audio_directory(self):
        self.output_dir = Path(__file__).parent / "audio"
        if not self.output_dir.exists():
            self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def load_personality(self):
        default_personality = {
            "voice": "alloy",
            "formality": 0.7,
            "tech_level": 0.8,
            "humor": 0.3
        }
        
        if self.personality_file.exists():
            try:
                with open(self.personality_file, 'r') as f:
                    self.personality = json.load(f)
            except:
                self.personality = default_personality
        else:
            self.personality = default_personality
    
    def save_personality(self):
        with open(self.personality_file, 'w') as f:
            json.dump(self.personality, f)
    
    def create_personality_slider(self, label_text, personality_key, row):
        label = ctk.CTkLabel(self.sidebar, text=label_text)
        label.grid(row=row, column=0, padx=20, pady=(10, 0))
        
        slider = ctk.CTkSlider(self.sidebar, from_=0, to=1, command=lambda value, key=personality_key: self.update_personality(key, value))
        slider.grid(row=row+1, column=0, padx=20, pady=(0, 10))
        slider.set(self.personality[personality_key])
    
    def update_personality(self, key, value):
        self.personality[key] = value
    
    def change_voice(self, voice):
        self.personality["voice"] = voice
    
    def append_message(self, message):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"{message}\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")
    
    def get_system_prompt(self):
        return f"""You are a cyber ninja AI assistant with the following personality traits:
- Formality Level: {self.personality['formality']:.1f} (0=casual, 1=formal)
- Technical Level: {self.personality['tech_level']:.1f} (0=simple, 1=technical)
- Humor Level: {self.personality['humor']:.1f} (0=serious, 1=humorous)
Adjust your responses according to these traits while maintaining a cyber ninja theme."""
    
    def send_message(self, event=None):
        message = self.chat_input.get().strip()
        if not message:
            return
        
        self.chat_input.delete(0, "end")
        self.append_message(f"You: {message}")
        
        try:
            # Get AI response
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.get_system_prompt()},
                    {"role": "user", "content": message}
                ]
            )
            reply = response.choices[0].message.content
            
            # Generate speech
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            speech_file_path = self.output_dir / f"response_{timestamp}.mp3"
            
            audio_response = self.client.audio.speech.create(
                model="tts-1",
                voice=self.personality["voice"],
                input=reply
            )
            
            with open(speech_file_path, 'wb') as f:
                for chunk in audio_response.iter_bytes():
                    f.write(chunk)
            
            self.append_message(f"Cyber Ninja AI: {reply}")
            self.current_audio = str(speech_file_path)
            self.play_audio()
            
        except Exception as e:
            self.append_message(f"Error: {str(e)}")
    
    def play_audio(self):
        if self.current_audio and os.path.exists(self.current_audio):
            pygame.mixer.music.load(self.current_audio)
            pygame.mixer.music.play()
            self.is_playing = True
            self.play_button.configure(text="⏸")
    
    def toggle_audio(self):
        if not self.current_audio:
            return
            
        if self.is_playing:
            pygame.mixer.music.pause()
            self.play_button.configure(text="▶")
        else:
            pygame.mixer.music.unpause()
            self.play_button.configure(text="⏸")
        self.is_playing = not self.is_playing
    
    def stop_audio(self):
        if self.current_audio:
            pygame.mixer.music.stop()
            self.is_playing = False
            self.play_button.configure(text="▶")

if __name__ == "__main__":
    app = CyberNinjaGUI()
    app.mainloop() 