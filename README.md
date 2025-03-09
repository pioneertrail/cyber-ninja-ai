# Cyber Ninja AI Assistant 🥷🤖

A modern, customizable AI chatbot with text-to-speech capabilities and a cyber ninja personality. Built with OpenAI's GPT-4 and TTS APIs.

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features 🚀

- 💬 Advanced AI chat powered by GPT-4
- 🎙️ Text-to-speech with multiple voice options
- 🎨 Modern GUI with dark/light theme support
- 🎮 Customizable personality traits
- 🎵 Integrated audio player with controls
- 💾 Save/load chat history
- ⚙️ Persistent settings

### Personality Customization
- Formality Level
- Technical Knowledge
- Humor
- Creativity
- Empathy
- Efficiency

### Voice Options
- Multiple voice choices (alloy, echo, fable, onyx, nova, shimmer)
- Adjustable speech speed
- Volume control

## Installation 📦

1. Clone the repository:
```bash
git clone https://github.com/yourusername/cyber-ninja-ai.git
cd cyber-ninja-ai
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Usage 🎮

Run the enhanced GUI version:
```bash
python enhanced_gui_chatbot.py
```

### Interface Guide

1. **Main Chat Area**
   - Type messages in the input field
   - Press Enter or click Send
   - View conversation history

2. **Sidebar Controls**
   - Theme selection (System/Dark/Light)
   - Voice settings
   - Personality trait sliders
   - Custom system prompt editor

3. **Audio Controls**
   - Play/Pause button
   - Stop button
   - Volume slider

4. **Chat Management**
   - Save chat history
   - Load previous chats
   - Save custom settings

## Configuration ⚙️

All settings are automatically saved in `settings.json` and include:
- Theme preference
- Voice selection
- Voice speed
- Volume level
- Personality traits
- Custom system prompt

## Requirements 📋

- Python 3.8+
- OpenAI API key
- Required packages (see requirements.txt):
  - openai
  - python-dotenv
  - customtkinter
  - pygame
  - pillow
  - darkdetect

## Contributing 🤝

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments 🙏

- OpenAI for GPT-4 and TTS APIs
- CustomTkinter for the modern GUI framework
- All contributors and users of this project 