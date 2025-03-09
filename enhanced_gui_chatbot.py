import customtkinter as ctk
from openai import OpenAI
import os
from dotenv import load_dotenv
from pathlib import Path
import pygame
import json
from datetime import datetime
import darkdetect
from tkinter import filedialog
import threading

class CyberNinjaGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Initialize OpenAI and audio
        load_dotenv()
        self.client = OpenAI()
        self.setup_audio_directory()
        pygame.mixer.init()
        
        # Load or create settings
        self.settings_file = Path(__file__).parent / "settings.json"
        self.load_settings()
        
        # Configure window
        self.title("Cyber Ninja AI Assistant")
        self.geometry("1000x700")
        
        # Configure grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Create sidebar frame
        self.sidebar = ctk.CTkScrollableFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        
        # Personality settings in sidebar
        self.create_sidebar_widgets()
        
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
        self.create_audio_controls()
        
        # Initialize state
        self.current_audio = None
        self.is_playing = False
        self.chat_history = []
        
        # Welcome message
        self.append_message("Cyber Ninja AI: Welcome, user. I am your cyber ninja assistant. How may I assist you today?")
        
        # Apply initial theme
        self.apply_theme()
    
    def create_sidebar_widgets(self):
        # Theme selection
        self.theme_label = ctk.CTkLabel(self.sidebar, text="Theme Settings", font=ctk.CTkFont(size=20, weight="bold"))
        self.theme_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        themes = ["System", "Dark", "Light"]
        self.theme_option = ctk.CTkOptionMenu(self.sidebar, values=themes, command=self.change_theme)
        self.theme_option.grid(row=1, column=0, padx=20, pady=(0, 10))
        self.theme_option.set(self.settings["theme"])
        
        # Voice settings
        self.voice_label = ctk.CTkLabel(self.sidebar, text="Voice Settings", font=ctk.CTkFont(size=20, weight="bold"))
        self.voice_label.grid(row=2, column=0, padx=20, pady=(20, 10))
        
        # Voice selection
        self.voice_option = ctk.CTkOptionMenu(self.sidebar, values=["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
                                            command=self.change_voice)
        self.voice_option.grid(row=3, column=0, padx=20, pady=(0, 10))
        self.voice_option.set(self.settings["voice"])
        
        # Voice speed
        self.speed_label = ctk.CTkLabel(self.sidebar, text="Voice Speed")
        self.speed_label.grid(row=4, column=0, padx=20, pady=(10, 0))
        self.speed_slider = ctk.CTkSlider(self.sidebar, from_=0.5, to=2.0, command=self.update_voice_speed)
        self.speed_slider.grid(row=5, column=0, padx=20, pady=(0, 10))
        self.speed_slider.set(self.settings["voice_speed"])
        
        # Personality traits
        self.personality_label = ctk.CTkLabel(self.sidebar, text="Personality Traits", font=ctk.CTkFont(size=20, weight="bold"))
        self.personality_label.grid(row=6, column=0, padx=20, pady=(20, 10))
        
        traits = [
            ("Formality", "formality"),
            ("Tech Level", "tech_level"),
            ("Humor", "humor"),
            ("Creativity", "creativity"),
            ("Empathy", "empathy"),
            ("Efficiency", "efficiency")
        ]
        
        for i, (label, key) in enumerate(traits):
            self.create_personality_slider(label, key, 7 + i*2)
        
        # Custom prompt editor
        self.prompt_label = ctk.CTkLabel(self.sidebar, text="Custom System Prompt", font=ctk.CTkFont(size=20, weight="bold"))
        self.prompt_label.grid(row=19, column=0, padx=20, pady=(20, 10))
        
        self.prompt_editor = ctk.CTkTextbox(self.sidebar, height=100)
        self.prompt_editor.grid(row=20, column=0, padx=20, pady=(0, 10))
        self.prompt_editor.insert("1.0", self.settings["custom_prompt"])
        
        # Chat history controls
        self.history_frame = ctk.CTkFrame(self.sidebar)
        self.history_frame.grid(row=21, column=0, padx=20, pady=(20, 10))
        
        self.save_history_button = ctk.CTkButton(self.history_frame, text="Save Chat", command=self.save_chat_history)
        self.save_history_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.load_history_button = ctk.CTkButton(self.history_frame, text="Load Chat", command=self.load_chat_history)
        self.load_history_button.grid(row=0, column=1, padx=5, pady=5)
        
        # Save settings button
        self.save_button = ctk.CTkButton(self.sidebar, text="Save Settings", command=self.save_settings)
        self.save_button.grid(row=22, column=0, padx=20, pady=(20, 10))
    
    def create_audio_controls(self):
        self.play_button = ctk.CTkButton(self.player_frame, text="▶", width=40, command=self.toggle_audio)
        self.play_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.stop_button = ctk.CTkButton(self.player_frame, text="⏹", width=40, command=self.stop_audio)
        self.stop_button.grid(row=0, column=1, padx=5, pady=5)
        
        self.volume_slider = ctk.CTkSlider(self.player_frame, from_=0, to=1, command=self.update_volume)
        self.volume_slider.grid(row=0, column=2, padx=20, pady=5)
        self.volume_slider.set(self.settings["volume"])
    
    def load_settings(self):
        default_settings = {
            "theme": "System",
            "voice": "alloy",
            "voice_speed": 1.0,
            "volume": 0.7,
            "formality": 0.7,
            "tech_level": 0.8,
            "humor": 0.3,
            "creativity": 0.6,
            "empathy": 0.5,
            "efficiency": 0.7,
            "custom_prompt": "You are a cyber ninja AI assistant. Maintain the cyber ninja theme while adjusting to the personality traits."
        }
        
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    self.settings = json.load(f)
            except:
                self.settings = default_settings
        else:
            self.settings = default_settings
    
    def save_settings(self):
        self.settings["custom_prompt"] = self.prompt_editor.get("1.0", "end-1c")
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f)
    
    def create_personality_slider(self, label_text, personality_key, row):
        label = ctk.CTkLabel(self.sidebar, text=label_text)
        label.grid(row=row, column=0, padx=20, pady=(10, 0))
        
        slider = ctk.CTkSlider(self.sidebar, from_=0, to=1, command=lambda value, key=personality_key: self.update_personality(key, value))
        slider.grid(row=row+1, column=0, padx=20, pady=(0, 10))
        slider.set(self.settings[personality_key])
    
    def update_personality(self, key, value):
        self.settings[key] = value
    
    def change_voice(self, voice):
        self.settings["voice"] = voice
    
    def update_voice_speed(self, speed):
        self.settings["voice_speed"] = speed
    
    def update_volume(self, volume):
        self.settings["volume"] = volume
        pygame.mixer.music.set_volume(volume)
    
    def change_theme(self, theme):
        self.settings["theme"] = theme
        self.apply_theme()
    
    def apply_theme(self):
        theme = self.settings["theme"]
        if theme == "System":
            theme = "Dark" if darkdetect.isDark() else "Light"
        
        ctk.set_appearance_mode(theme)
    
    def save_chat_history(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.chat_history, f, ensure_ascii=False, indent=2)
    
    def load_chat_history(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.chat_history = json.load(f)
            
            self.chat_display.configure(state="normal")
            self.chat_display.delete("1.0", "end")
            for message in self.chat_history:
                self.chat_display.insert("end", f"{message}\n")
            self.chat_display.configure(state="disabled")
            self.chat_display.see("end")
    
    def append_message(self, message):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"{message}\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")
        self.chat_history.append(message)
    
    def get_system_prompt(self):
        base_prompt = self.prompt_editor.get("1.0", "end-1c")
        personality_traits = "\n".join([
            f"- {key.replace('_', ' ').title()}: {value:.1f}"
            for key, value in self.settings.items()
            if key in ["formality", "tech_level", "humor", "creativity", "empathy", "efficiency"]
        ])
        return f"{base_prompt}\n\nPersonality Traits:\n{personality_traits}"
    
    def send_message(self, event=None):
        message = self.chat_input.get().strip()
        if not message:
            return
        
        self.chat_input.delete(0, "end")
        self.append_message(f"You: {message}")
        
        # Disable input while processing
        self.chat_input.configure(state="disabled")
        self.send_button.configure(state="disabled")
        
        # Create a thread for API calls
        thread = threading.Thread(target=self.process_message, args=(message,))
        thread.start()
    
    def process_message(self, message):
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
                voice=self.settings["voice"],
                speed=self.settings["voice_speed"],
                input=reply
            )
            
            with open(speech_file_path, 'wb') as f:
                for chunk in audio_response.iter_bytes():
                    f.write(chunk)
            
            self.append_message(f"Cyber Ninja AI: {reply}")
            self.current_audio = str(speech_file_path)
            
            # Play audio in main thread
            self.after(0, self.play_audio)
            
        except Exception as e:
            self.append_message(f"Error: {str(e)}")
        
        finally:
            # Re-enable input
            self.after(0, lambda: self.chat_input.configure(state="normal"))
            self.after(0, lambda: self.send_button.configure(state="normal"))
            self.after(0, lambda: self.chat_input.focus())
    
    def play_audio(self):
        if self.current_audio and os.path.exists(self.current_audio):
            pygame.mixer.music.load(self.current_audio)
            pygame.mixer.music.set_volume(self.settings["volume"])
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
    
    def setup_audio_directory(self):
        self.output_dir = Path(__file__).parent / "audio"
        if not self.output_dir.exists():
            self.output_dir.mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    app = CyberNinjaGUI()
    app.mainloop() 