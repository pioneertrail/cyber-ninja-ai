import customtkinter as ctk
from openai import OpenAI
import os
from dotenv import load_dotenv, set_key
from pathlib import Path
import pygame
import json
from datetime import datetime
import darkdetect
from tkinter import filedialog
import threading

class APIKeyDialog(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("OpenAI API Key Setup")
        self.geometry("400x200")
        
        # Center the window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
        # Make it modal
        self.transient(self.master)
        self.grab_set()
        
        # Add widgets
        self.label = ctk.CTkLabel(self, text="Please enter your OpenAI API key:", font=ctk.CTkFont(size=14))
        self.label.pack(pady=(20, 10))
        
        self.api_key = ctk.CTkEntry(self, width=300, show="•")
        self.api_key.pack(pady=10)
        
        self.show_key = ctk.CTkCheckBox(self, text="Show API Key", command=self.toggle_key_visibility)
        self.show_key.pack(pady=10)
        
        self.submit_button = ctk.CTkButton(self, text="Save API Key", command=self.save_key)
        self.submit_button.pack(pady=10)
        
        self.result = None
    
    def toggle_key_visibility(self):
        self.api_key.configure(show="" if self.show_key.get() else "•")
    
    def save_key(self):
        self.result = self.api_key.get()
        self.destroy()

class CyberNinjaGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Initialize paths and settings
        self.setup_paths()
        if not self.check_api_key():
            self.get_api_key()
        self.initialize_client()
        pygame.mixer.init()
        self.settings_file = Path(__file__).parent / "settings.json"
        self.load_settings()
        
        # Configure window
        self.title("Cyber Ninja AI Assistant")
        self.geometry("1200x800")  # Larger default size
        
        # Configure grid layout with better spacing
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)  # Give more weight to chat area
        
        # Create sidebar with better styling
        self.sidebar = ctk.CTkScrollableFrame(
            self,
            width=300,  # Wider sidebar
            corner_radius=10,
            fg_color="transparent"
        )
        self.sidebar.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        # Create main content area with better organization
        self.main_content = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.main_content.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_content.grid_rowconfigure(0, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)
        
        # Create header frame for API key button
        self.header_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.create_menu()
        
        # Create chat frame with better styling
        self.chat_frame = ctk.CTkFrame(self.main_content, corner_radius=10)
        self.chat_frame.grid(row=1, column=0, sticky="nsew")
        self.chat_frame.grid_rowconfigure(0, weight=1)
        self.chat_frame.grid_columnconfigure(0, weight=1)
        
        # Create chat display with better styling
        self.chat_display = ctk.CTkTextbox(
            self.chat_frame,
            corner_radius=10,
            font=ctk.CTkFont(size=13)
        )
        self.chat_display.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.chat_display.configure(state="disabled")
        
        # Create input area with better styling
        self.input_frame = ctk.CTkFrame(self.main_content, corner_radius=10)
        self.input_frame.grid(row=2, column=0, sticky="ew", pady=(20, 0))
        self.input_frame.grid_columnconfigure(0, weight=1)
        
        # Chat input with better styling
        self.chat_input = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Type your message here...",
            height=40,
            font=ctk.CTkFont(size=13)
        )
        self.chat_input.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="ew")
        self.chat_input.bind("<Return>", self.send_message)
        
        # Send button with better styling
        self.send_button = ctk.CTkButton(
            self.input_frame,
            text="Send",
            width=100,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.send_button.grid(row=0, column=1, padx=(0, 20), pady=20)
        self.send_button.configure(command=self.send_message)
        
        # Audio player with better styling
        self.player_frame = ctk.CTkFrame(self.main_content, corner_radius=10)
        self.player_frame.grid(row=3, column=0, sticky="ew", pady=(20, 0))
        self.create_audio_controls()
        
        # Create sidebar content with better organization
        self.create_sidebar_widgets()
        
        # Initialize state
        self.current_audio = None
        self.is_playing = False
        self.chat_history = []
        
        # Welcome message
        self.append_message("Cyber Ninja AI: Welcome, user. I am your cyber ninja assistant. How may I assist you today?")
        
        # Apply theme
        self.apply_theme()
    
    def setup_paths(self):
        self.base_dir = Path(__file__).parent.absolute()
        self.output_dir = self.base_dir / "audio"
        self.env_file = self.base_dir / ".env"
        self.output_dir.mkdir(exist_ok=True)
    
    def check_api_key(self):
        load_dotenv(self.env_file)
        return bool(os.getenv("OPENAI_API_KEY"))
    
    def get_api_key(self):
        dialog = APIKeyDialog()
        self.wait_window(dialog)
        if dialog.result:
            # Save to .env file
            with open(self.env_file, "w") as f:
                f.write(f"OPENAI_API_KEY={dialog.result}")
            os.environ["OPENAI_API_KEY"] = dialog.result
        else:
            self.quit()
    
    def initialize_client(self):
        load_dotenv(self.env_file)
        self.client = OpenAI()
    
    def create_menu(self):
        self.api_button = ctk.CTkButton(
            self.header_frame,
            text="Change API Key",
            width=120,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            border_width=1
        )
        self.api_button.pack(side="right", padx=10)
        self.api_button.configure(command=self.change_api_key)
    
    def change_api_key(self):
        dialog = APIKeyDialog()
        self.wait_window(dialog)
        if dialog.result:
            # Update .env file
            with open(self.env_file, "w") as f:
                f.write(f"OPENAI_API_KEY={dialog.result}")
            os.environ["OPENAI_API_KEY"] = dialog.result
            self.initialize_client()
            self.append_message("Cyber Ninja AI: API key updated successfully!")
    
    def create_sidebar_widgets(self):
        # Theme settings with better styling
        self.create_section_header("Theme Settings", 0)
        themes = ["System", "Dark", "Light"]
        self.theme_option = self.create_dropdown(themes, self.change_theme, 1)
        self.theme_option.set(self.settings["theme"])
        
        # Voice settings with better styling
        self.create_section_header("Voice Settings", 2)
        voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        self.voice_option = self.create_dropdown(voices, self.change_voice, 3)
        self.voice_option.set(self.settings["voice"])
        
        # Voice speed with better styling
        self.create_slider_with_label("Voice Speed", 4, "voice_speed", 0.5, 2.0)
        
        # Personality traits with better styling
        self.create_section_header("Personality Traits", 6)
        traits = [
            ("Formality", "formality"),
            ("Tech Level", "tech_level"),
            ("Humor", "humor"),
            ("Creativity", "creativity"),
            ("Empathy", "empathy"),
            ("Efficiency", "efficiency")
        ]
        
        for i, (label, key) in enumerate(traits):
            self.create_slider_with_label(label, 7 + i*2, key, 0, 1)
        
        # Custom prompt with better styling
        self.create_section_header("Custom System Prompt", 19)
        self.prompt_editor = ctk.CTkTextbox(
            self.sidebar,
            height=100,
            font=ctk.CTkFont(size=12)
        )
        self.prompt_editor.grid(row=20, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.prompt_editor.insert("1.0", self.settings["custom_prompt"])
        
        # Chat controls with better styling
        self.create_section_header("Chat Controls", 21)
        self.create_chat_controls(22)
        
        # Save settings with better styling
        self.save_button = ctk.CTkButton(
            self.sidebar,
            text="Save Settings",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=40
        )
        self.save_button.grid(row=23, column=0, padx=20, pady=(20, 20), sticky="ew")
        self.save_button.configure(command=self.save_settings)
    
    def create_section_header(self, text, row):
        label = ctk.CTkLabel(
            self.sidebar,
            text=text,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        label.grid(row=row, column=0, padx=20, pady=(20, 10), sticky="w")
    
    def create_dropdown(self, values, command, row):
        dropdown = ctk.CTkOptionMenu(
            self.sidebar,
            values=values,
            command=command,
            font=ctk.CTkFont(size=13),
            height=32
        )
        dropdown.grid(row=row, column=0, padx=20, pady=(0, 10), sticky="ew")
        return dropdown
    
    def create_slider_with_label(self, label_text, row, key, min_val, max_val):
        label = ctk.CTkLabel(
            self.sidebar,
            text=label_text,
            font=ctk.CTkFont(size=13)
        )
        label.grid(row=row, column=0, padx=20, pady=(10, 0), sticky="w")
        
        slider = ctk.CTkSlider(
            self.sidebar,
            from_=min_val,
            to=max_val,
            command=lambda value, k=key: self.update_personality(k, value)
        )
        slider.grid(row=row+1, column=0, padx=20, pady=(5, 10), sticky="ew")
        slider.set(self.settings[key])
    
    def create_chat_controls(self, row):
        control_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        control_frame.grid(row=row, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        save_btn = ctk.CTkButton(
            control_frame,
            text="Save Chat",
            font=ctk.CTkFont(size=13),
            height=32,
            command=self.save_chat_history
        )
        save_btn.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="ew")
        
        load_btn = ctk.CTkButton(
            control_frame,
            text="Load Chat",
            font=ctk.CTkFont(size=13),
            height=32,
            command=self.load_chat_history
        )
        load_btn.grid(row=0, column=1, padx=(5, 0), pady=5, sticky="ew")
        control_frame.grid_columnconfigure(0, weight=1)
        control_frame.grid_columnconfigure(1, weight=1)
    
    def create_audio_controls(self):
        # Play button with better styling
        self.play_button = ctk.CTkButton(
            self.player_frame,
            text="▶",
            width=40,
            height=40,
            font=ctk.CTkFont(size=16)
        )
        self.play_button.grid(row=0, column=0, padx=(20, 5), pady=20)
        self.play_button.configure(command=self.toggle_audio)
        
        # Stop button with better styling
        self.stop_button = ctk.CTkButton(
            self.player_frame,
            text="⏹",
            width=40,
            height=40,
            font=ctk.CTkFont(size=16)
        )
        self.stop_button.grid(row=0, column=1, padx=5, pady=20)
        self.stop_button.configure(command=self.stop_audio)
        
        # Volume slider with better styling
        self.volume_slider = ctk.CTkSlider(
            self.player_frame,
            from_=0,
            to=1,
            command=self.update_volume,
            width=200
        )
        self.volume_slider.grid(row=0, column=2, padx=(20, 20), pady=20, sticky="ew")
        self.volume_slider.set(self.settings["volume"])
        
        self.player_frame.grid_columnconfigure(2, weight=1)
    
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

if __name__ == "__main__":
    app = CyberNinjaGUI()
    app.mainloop() 