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

    while conversation_active:
        # MAIN DIALOG LOOP
        # User initial input
        if DEBUG:
            # user_query = 'I want to make a booking for 4 people today in Warsaw center.'
            user_query = input('User: ')
            # print(f'USER: {user_query}')
        else:
            print('Listening')
            user_query = stt.record_audio()
            print(f'USER: {user_query}')

        # Check for exit command
        if user_query.lower() in ['exit', 'quit', 'stop', 'goodbye', 'bye']:
            farewell = assistant.generate_response('farewell', intents)
            print(f'ASSISTANT: {farewell}')
            if not DEBUG:
                tts.generate_audio(farewell)
            conversation_active = False
            continue

        # 1. Start with checking which info are we still missing
        missing_info = conversation_manager.check_missing_info()
        print(f'MISSING: {missing_info}')

        # 2. If missing info, ask the questions
        if missing_info:
            next_question = missing_info[0]
            question = assistant.generate_response(next_question, intents)
            print(f'ASSISTANT: {question}')
            if not DEBUG:
                tts.generate_audio(question)


        try:
            intent, extracted_info = assistant.recognize_intent(user_query, intents_categories)
            entities = assistant.recognize_entity(user_query)

            # Update dialog manager with all extra info from the input
            conversation_manager.extract_info(extracted_info)
            missing_info = conversation_manager.check_missing_info()

            if not missing_info and not conversation_manager.recommended_restaurant:
                recommended_restaurant = recommend_restaurant({
                    "dietary": conversation_manager.dietary_preferences,
                    "cuisine": conversation_manager.culinary_preferences,
                    "party_size": conversation_manager.party_size,
                    "booking_time": conversation_manager.booking_date_time
                })

                conversation_manager.recommended_restaurant = recommended_restaurant

                recommendation_response = assistant.generate_response("provide_recommendation", intents)
                response = conversation_manager.fill_template(recommendation_response)

            elif intent == "booking_confirmation" and conversation_manager.recommended_restaurant:
                # Confirming the booking
                confirmation_response = assistant.generate_response("booking_confirmation", intents)
                response = conversation_manager.fill_template(confirmation_response)

            elif intent == "confirm_details":
                # Confirm the information we have
                confirm_response = assistant.generate_response("confirm_details", intents)
                response = conversation_manager.fill_template(confirm_response)

            else:
                # Regular response based on intent
                response = assistant.generate_response(intent, intents)
                response = conversation_manager.fill_template(response)

            print(f"ASSISTANT: {response}")
            if not DEBUG:
                tts.generate_audio(response)

        except Exception as e:
            # Error handling
            print(f'ERROR: {e}')
            fallback_response = assistant.generate_response('fallback', intents)
            print(f'ASSISTANT: {fallback_response}')
            if not DEBUG:
                tts.generate_audio(fallback_response)

        break


if __name__ == '__main__':
    main()
