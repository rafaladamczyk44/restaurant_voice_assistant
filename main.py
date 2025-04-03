import yaml
from speech_to_text import STT
from assistant_nlu import Assistant
from converstaion_manager import ConversationManager

DEBUG = True

stt = STT()
assistant = Assistant()
conversation_manager = ()

with open('intents.yaml', 'r') as file:
    intents = yaml.safe_load(file)

intents_categories = list(intents.keys())

# while True:

if DEBUG:
    user_query = 'I want to make a booking for 4 people today'
else:
    user_query = stt.record_audio()

try:
    print(f'User said: {user_query}')
    intent_recognized, extra_info = assistant.recognize_intent(user_query, intents_categories)
    print(f'Intent recognized: {intent_recognized}')
    print(f'Extra info extracted: {extra_info}')

    response_to_user = assistant.generate_response(intent_recognized, intents)
    print(f'SYSTEM: {response_to_user}')
except Exception as e:
    print('Couldnt recognize the intent :(')


