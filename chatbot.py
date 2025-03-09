from openai import OpenAI
import os
from dotenv import load_dotenv
from pathlib import Path
import stat

class CyberNinjaChatbot:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI()
        try:
            # Get the absolute path to the script's directory
            base_dir = Path(__file__).resolve().parent
            self.output_dir = base_dir / "audio"
            
            # Create directory with full permissions if it doesn't exist
            if not self.output_dir.exists():
                self.output_dir.mkdir(parents=True, exist_ok=True)
                # Set directory permissions
                if os.name == 'nt':  # Windows
                    try:
                        os.chmod(self.output_dir, 0o777)
                    except Exception as perm_error:
                        print(f"Warning: Could not set directory permissions: {perm_error}")
            print(f"Audio output directory: {self.output_dir}")
        except Exception as e:
            print(f"Error setting up audio directory: {e}")
            raise
        
    def get_chat_response(self, prompt):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",  # Using gpt-4 as gpt-4o was not found in documentation
                messages=[
                    {"role": "system", "content": "You are a cyber ninja AI assistant with advanced capabilities. Respond in a high-tech, professional manner."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating chat response: {e}")
            return "System error encountered. Please try again."

    def text_to_speech(self, text, filename="response.mp3"):
        try:
            # Ensure unique filename to avoid permission issues
            counter = 0
            while True:
                if counter == 0:
                    speech_file_path = self.output_dir / filename
                else:
                    base, ext = os.path.splitext(filename)
                    speech_file_path = self.output_dir / f"{base}_{counter}{ext}"
                
                if not speech_file_path.exists():
                    break
                counter += 1

            # Generate speech
            response = self.client.audio.speech.create(
                model="tts-1",
                voice="alloy",  # Using alloy for cyber ninja style
                input=text
            )

            # Write with explicit permissions
            with open(speech_file_path, 'wb') as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)
            
            # Set file permissions
            try:
                os.chmod(speech_file_path, 0o666)  # Read/write for everyone
            except Exception as perm_error:
                print(f"Warning: Could not set file permissions: {perm_error}")
            
            return speech_file_path
        except Exception as e:
            print(f"Error generating speech: {e}")
            return None

    def play_audio(self, file_path):
        try:
            if os.name == 'nt':  # Windows
                # Use quotes around the path to handle spaces
                os.system(f'start "" "{file_path.absolute()}"')
            elif os.name == 'posix':  # macOS/Linux
                os.system(f'afplay "{file_path}"')
        except Exception as e:
            print(f"Error playing audio: {e}")

    def run(self):
        print("Cyber Ninja AI: Online. Type 'exit' to terminate session.")
        while True:
            try:
                user_input = input("\nYou: ")
                if user_input.lower() == 'exit':
                    print("Cyber Ninja AI: Terminating session. Goodbye.")
                    break
                
                reply = self.get_chat_response(user_input)
                print(f"\nCyber Ninja AI: {reply}")
                
                audio_file = self.text_to_speech(reply)
                if audio_file:
                    self.play_audio(audio_file)
            except KeyboardInterrupt:
                print("\nCyber Ninja AI: Detected interrupt signal. Shutting down gracefully.")
                break
            except Exception as e:
                print(f"\nCyber Ninja AI: An error occurred: {e}")
                print("Continuing operation...")

if __name__ == "__main__":
    try:
        bot = CyberNinjaChatbot()
        bot.run()
    except Exception as e:
        print(f"Fatal error: {e}") 