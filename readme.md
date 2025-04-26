# Restaurant Booking Voice Assistant

A voice assistant that helps users find and book restaurants based on their preferences. The assistant uses natural language processing to understand user queries, extract relevant information, and recommend suitable restaurants.

## Prerequisites

- Python 3.10+
- OpenAI API Key (for GPT-4o-mini and TTS-1)
- Google Places API Key

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/restaurant-booking-voice-assistant.git
cd restaurant-booking-voice-assistant
```

2. Create and activate a virtual environment:
```
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install the required packages:
```
pip install -r requirements.txt
```

## Setup API Keys

Set your API keys as environment variables:

```bash
export OPENAI_KEY="your_openai_api_key"
export GOOGLE_KEY="your_google_places_api_key"
```

## Project Structure

- `main.py` - Main application entry point and dialogue flow controller
- `speech_to_text.py` - Handles voice input using Whisper model
- `text_to_speech.py` - Handles voice output using OpenAI TTS-1
- `assistant_nlu.py` - Natural Language Understanding component using GPT-4o-mini
- `conversation_manager.py` - Manages conversation state and user information
- `intents.yaml` - Contains response templates for different intents

## Running the Application

Run in debug mode (with text input instead of voice):
```
python main.py
```

Run the application in regular mode (with voice input/output):
```
python main.py --no-debug
```

## Components

1. **Speech-to-Text (STT)**: Uses OpenAI's Whisper model to convert user's voice to text.

2. **Text-to-Speech (TTS)**: Uses OpenAI's TTS-1 to convert text responses to voice.

3. **Natural Language Understanding (NLU)**: Uses GPT-4o-mini to:
   - Recognize user intents
   - Extract information (dietary preferences, cuisine type, party size, etc.)
   - Generate API queries for restaurant search
   - Create personalized restaurant recommendations

4. **Conversation Manager**: Keeps track of the conversation state, collected information, and user confirmation.

5. **Restaurant Search**: Uses Google Places API to find restaurants matching user preferences.

## Data Storage

User data is stored in SQLite databases in the `user_data` directory. Each conversation is saved with a timestamp and a hashed user identifier.

## Notes

- The system requires a network connection for API calls to OpenAI and Google Places.
- Audio quality may affect speech recognition performance.
- For privacy, user names are hashed before storage.