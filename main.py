import os
import yaml
import random

from speech_to_text import STT
from text_to_speech import TTS
from assistant_nlu import Assistant
from converstaion_manager import ConversationManager


def recommend_restaurant(user_preferences):
    """
    Placeholder for the actual recommendation system
    :param user_preferences:
    :return:
    """
    placeholder_restaurants = [
        {"name": "The Green Garden", "cuisine": "Mediterranean", "dietary": "Vegetarian"},
        {"name": "Spice Route", "cuisine": "Indian", "dietary": "Vegan options"},
        {"name": "Pasta Paradise", "cuisine": "Italian", "dietary": "Gluten-free options"}
    ]
    return random.choice(placeholder_restaurants)

# For testing so I dont have to speak everytime
DEBUG = True

# Initialize all my classes
stt = STT()
tts = TTS()
assistant = Assistant()
conversation_manager = ConversationManager()

with open('intents.yaml', 'r') as file:
    intents = yaml.safe_load(file)

intents_categories = list(intents.keys())


def main():

    # Greeting to the user opening the app
    greetings_response = assistant.generate_response('greetings', intents)
    print(f'ASSISTANT: {greetings_response}')
    if not DEBUG:
        tts.generate_audio(greetings_response)

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
            intent, extracted_info = assistant.recognize_intent(user_query, intents_categories)
            print(f'Extracted info: {extracted_info}')

            # Update dialog manager with all extra info from the input
            conversation_manager.extract_info(extracted_info)

            # Check missing info and ask
            missing_info = conversation_manager.check_missing_info()
            print(f'MISSING INFO: {missing_info}')

            if missing_info:
                response = assistant.generate_response(missing_info[0], intents)
                if DEBUG:
                    print(f'ASSISTANT: {response}')
                else:
                    tts.generate_audio(response)
            else:
                print('I believe I have all information now')
                conversation_active = False

        except Exception as e:
            print(f'ERROR: {e}, {type(e)}')
            fallback_response = assistant.generate_response('fallback', intents)

            if DEBUG:
                print(f'ASSISTANT: {fallback_response}')
            else:
                tts.generate_audio(fallback_response)

    booking_confirmation = f"""
    Time of booking: {conversation_manager.booking_date_time},
    Booking in the name of {conversation_manager.user_name},
    Preferred cuisine: {conversation_manager.culinary_preferences},
    Dietary: {conversation_manager.dietary_preferences},
    Party size: {conversation_manager.party_size},
    I will look for the restaurants in the area of: {conversation_manager.booking_location}.
    
    Can you please confirm if the details are correct?
    """
    if DEBUG:
        print(booking_confirmation)
    else:
        tts.generate_audio(booking_confirmation)


if __name__ == '__main__':
    main()
