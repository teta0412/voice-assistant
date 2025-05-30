# Voice Assistant with Wake Word Detection

A production-ready voice assistant built with LiveKit, OpenAI, and wake word detection capabilities. The system listens for wake words and activates a conversational AI agent that can process voice commands and respond naturally. It worked on Raspberry Pi 4 Model B with super fast response

## Architecture Overview

The application consists of two main components:

- **Wake Word Detection (`wake_word.py`)**: Continuously listens for wake words using OpenWakeWord
- **Voice Agent (`agent.py`)**: Handles conversation using LiveKit's real-time voice capabilities with OpenAI GPT-4o-mini, Deepgram STT, and Cartesia TTS

## Prerequisites

- Ubuntu Server 2024 LTS or any OS with correct configure
- Python 3.10 or higher (Optional not tested < 3.10)
- Audio input device (microphone prefer 16kHz like pretrained sample rate or have to config lib of Livekit and resample of openWakeWord )
- Audio output device (speaker or sth else )
- Internet connection for API services

## Installation

### 1. System Dependencies

Update your system and install required packages:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.10-venv portaudio19-dev python3-pyaudio
```

### 2. Clone and Setup Project

```bash
# Clone your repository (replace with your actual repo URL)
git clone <your-repository-url>
cd voice-assistant

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download Livekit Requirements

```bash
python agent.py download-files
```

## Configuration

### 1. Environment Variables

Copy the example environment file and configure your API keys:

```bash
cp env.example .env
```

Edit `.env` with your actual API credentials:

```env
DEEPGRAM_API_KEY=your_deepgram_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
CARTESIA_API_KEY=your_cartesia_api_key_here
LIVEKIT_API_KEY=your_livekit_api_key_here
LIVEKIT_API_SECRET=your_livekit_api_secret_here
LIVEKIT_URL=wss://voice-assistant-8oxmw0mi.livekit.cloud
```

### 2. Required API Keys

You'll need to obtain API keys from the following services:

- **Deepgram**: Sign up at [deepgram.com](https://deepgram.com) for speech-to-text
- **OpenAI**: Get your API key from [platform.openai.com](https://platform.openai.com)
- **Cartesia**: Register at [cartesia.ai](https://cartesia.ai) for text-to-speech
- **LiveKit**: Create an account at [livekit.io](https://livekit.io) for real-time voice processing

### 3. Audio Device Configuration

The system is configured to use audio input device ID `1`. To find your correct device ID:

```bash
python3 -c "
import pyaudio
p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    if info['maxInputChannels'] > 0:
        print(f'Device {i}: {info[\"name\"]}')
p.terminate()
"
```

Update the `INPUT_DEVICE_ID` variable in both `wake_word.py` and `agent.py` if needed.

## Usage

### Running the Voice Assistant

Activate the virtual environment and start the wake word detection:

```bash
source .venv/bin/activate
python wake_word.py
```

The system will:

1. **Listen for wake words** - Say any supported wake word (e.g., "Hey Jarvis", "Alexa", "Computer")
2. **Activate the agent** - The voice assistant will start and greet you
3. **Process conversations** - Speak naturally; the agent will respond
4. **Return to listening** - Say something meaning "end conversation" to return to wake word detection

### Supported Wake Words

The system uses OpenWakeWord's pre-trained models, which include:
- "Hey Jarvis"
- "Alexa" 
- "Hey Mycroft"
- And many others

### Voice Commands

Once activated, you can:
- Ask questions naturally
- Request assistance with various tasks
- Say something meaning "end conversation" to return to wake word listening

## Architecture Details

### Wake Word Detection
- **Framework**: OpenWakeWord with TensorFlow Lite
- **Audio Processing**: 48kHz → 16kHz resampling
- **Detection Threshold**: 0.5 confidence score
- **Models**: Pre-trained multilingual wake word models

### Voice Agent
- **STT**: Deepgram Nova-3 (multilingual)
- **LLM**: OpenAI GPT-4o-mini
- **TTS**: Cartesia (high-quality voice synthesis)
- **VAD**: Silero Voice Activity Detection
- **Turn Detection**: Multilingual model for conversation flow

### Key Features
- **Interruption Handling**: Disabled to prevent cut-offs during responses
- **Noise Cancellation**: LiveKit Cloud BVC noise cancellation
- **Multi-language Support**: Handles multiple languages automatically
- **Function Tools**: Extensible tool system for custom capabilities

## Troubleshooting

### Common Issues

**Audio Device Not Found**
```bash
# List available audio devices
arecord -l
# Test microphone
arecord -d 5 test.wav && aplay test.wav
```

**Permission Denied for Audio**
```bash
sudo usermod -a -G audio $USER
# Log out and back in
```

**Dependencies Installation Failed**
```bash
# Install build essentials
sudo apt install -y build-essential python3-dev
# Reinstall requirements
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

**Wake Word Not Detected**
- Ensure microphone is working and not muted
- Check `INPUT_DEVICE_ID` matches your microphone
- Speak clearly and at normal volume
- Try different wake words

**API Connection Issues**
- Verify all API keys are correctly set in `.env`
- Check internet connection
- Ensure API quotas haven't been exceeded

### Logging and Debugging

Enable verbose logging by modifying the scripts:

```python
# Add to the top of your scripts
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Production Deployment

### Running as a Service

Create a systemd service for automatic startup:

```ini
# /etc/systemd/system/voice-assistant.service
[Unit]
Description=Voice Assistant with Wake Word Detection
After=network.target sound.target

[Service]
Type=simple
User=your-username
Group=audio
WorkingDirectory=/path/to/voice-assistant
Environment=PATH=/path/to/voice-assistant/.venv/bin
ExecStart=/path/to/voice-assistant/.venv/bin/python wake_word.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable voice-assistant
sudo systemctl start voice-assistant
```

### Security Considerations

- Store API keys securely (consider using AWS Secrets Manager or similar)
- Run with minimal user privileges
- Monitor API usage and costs
- Implement rate limiting for production use
- Consider using environment-specific configurations

## Development

### Adding Custom Tools

Extend the agent with custom functions:

```python
@function_tool()
async def custom_function(context: RunContext, parameter: str):
    """Description of your custom function."""
    # Your implementation here
    return "Response"

# Add to Assistant class
class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="Your instructions here.",
            tools=[terminate_agent, custom_function]  # Add your tool
        )
```

### Configuration Options

Key configuration parameters in `agent.py`:
- `allow_interruptions`: Enable/disable interruption handling
- `model`: Change LLM model (gpt-4o-mini, gpt-4o, etc.)
- `language`: Set STT language preferences
- `chunk_size`: Adjust audio processing chunk size

## API Documentation

- [LiveKit Agents](https://docs.livekit.io/agents/)
- [OpenWakeWord](https://github.com/dscripka/openWakeWord)
- [Deepgram API](https://developers.deepgram.com/)
- [OpenAI API](https://platform.openai.com/docs/)
- [Cartesia API](https://cartesia.ai/docs/)

## Support

For issues and questions:
- Check the troubleshooting section above
- Review API service status pages
- Check audio device configuration
- Verify all dependencies are properly installed
- Email me: ducna0412@gmail.com
