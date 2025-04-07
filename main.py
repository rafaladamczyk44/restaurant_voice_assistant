import yaml

from speech_to_text import STT
from text_to_speech import TTS
from assistant_nlu import Assistant
from converstaion_manager import ConversationManager


def dialog_response(response):
    if DEBUG:
        print(f'ASSISTANT: {response}')
    else:
        tts.generate_audio(response)


def main():
    # Greeting to the user opening the app
    greetings_response = assistant.generate_response('greetings')
    dialog_response(greetings_response)

    conversation_active = True

    # MAIN dialog loop
    while conversation_active:
        try:
            # User input
            if DEBUG:
                user_query = input('User: ')
            else:
                print('Listening')
                user_query = stt.record_audio()
                print(f'USER: {user_query}')

            # Extracting information from user's input
            intent, extracted_info = assistant.recognize_intent(user_query)

            if intent == 'farewell':
                response = assistant.generate_response('farewell')
                dialog_response(response)
                conversation_active = False
                break

            if intent == 'fallback':
                response = assistant.generate_response('fallback')
                dialog_response(response)
            elif intent == 'greetings':
                response = assistant.generate_response('greetings')
                dialog_response(response)
            else:
                # print(f'DEBUG Intent recognized: {intent}')
                # print(f'DEBUG Extracted info: {extracted_info}')

                # Update dialog manager with all extra info from the input
                conversation_manager.extract_info(extracted_info)

                # Check missing info and ask
                missing_info = conversation_manager.check_missing_info()
                print(f'DEBUG Missing info: {missing_info}')

                if missing_info:
                    response = assistant.generate_response(missing_info[0])
                    dialog_response(response)
                else:
                    print('ASSISTANT: I believe I have all information now')
                    print(conversation_manager.return_details())
                    conversation_active = False

        except Exception as e:
            print(f'ERROR:{type(e)}, {e}' )
            response = f'ASSISTANT: I am sorry, there was a problem while processing your request. Please try again.'
            dialog_response(response)


if __name__ == '__main__':
    # For testing so I don't have to speak everytime
    DEBUG = True

    with open('intents.yaml', 'r') as file:
        intents = yaml.safe_load(file)

    intents_categories = list(intents.keys())

    # Initialize all my classes
    stt = STT()
    tts = TTS()
    assistant = Assistant(intents=intents, intent_categories=intents_categories)
    conversation_manager = ConversationManager()

    # Initialize the app
    main()