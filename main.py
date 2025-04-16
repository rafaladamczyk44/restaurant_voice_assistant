import os
import yaml
import requests

from speech_to_text import STT
from text_to_speech import TTS
from assistant_nlu import Assistant
from converstaion_manager import ConversationManager

GOOGLE_API_KEY = os.getenv('GOOGLE_KEY')

def find_restaurants(diet, cuisine, city, area) -> list:

    if diet == "No specific dietary preferences":
        diet = ""

    if cuisine == "No specific cuisine preferences":
        cuisine = ""

    query = f"{diet}, {cuisine} restaurants {area} {city}"

    text_search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

    params = {
        "query": query,
        "type": "restaurant",
        "key": GOOGLE_API_KEY
    }

    response = requests.get(text_search_url, params=params)

    if response.status_code != 200:
        print("Error:", response.status_code, response.text)
        return []

    places = response.json().get("results", [])
    places_sorted = sorted(places, key=lambda x: x.get('rating', 0), reverse=True)

    details_url = "https://maps.googleapis.com/maps/api/place/details/json"

    results = []

    for place in places_sorted:
        place_id = place["place_id"]

        details_params = {
            "place_id": place_id,
            "fields": "name,rating,formatted_address,review",
            "key": GOOGLE_API_KEY
        }

        details_response = requests.get(details_url, params=details_params)

        if details_response.status_code != 200:
            continue

        details = details_response.json().get("result", {})
        name = details.get("name")
        address = details.get("formatted_address")
        rating = details.get("rating")
        reviews = details.get("reviews", [])

        # Process reviews
        review_texts = []
        matched_keywords = []

        for review in reviews[:5]:
            text = review.get('text', '')
            review_texts.append(text)


        restaurant_data = {
            "name": name,
            "address": address,
            "rating": rating,
            "recent_reviews": review_texts,
            "matched_keywords": list(set(matched_keywords))  # avoid duplicates
        }

        results.append(restaurant_data)

    return results


def dialog_response(response):
    if DEBUG:
        print(f'ASSISTANT: {response}')
        # tts.generate_audio(response)
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

            last_question = conversation_manager.last_question

            # Extracting information from user's input
            intent, extracted_info = assistant.recognize_intent(user_query, last_question)

            conversation_manager.update_state(intent)  # Move to next state

            # Update dialog manager with all extra info from the input
            confirmation_prompt = conversation_manager.extract_info(extracted_info)
            if confirmation_prompt:
                dialog_response(confirmation_prompt)
                continue

            # Check if we're in confirmation mode first
            if conversation_manager.current_confirm_field:
                yesses = ['yes', 'correct', 'yup', 'yeah', 'ok', 'right']
                nopes = ['no', 'nope', 'wrong', 'incorrect']

                user_input_to_check = user_query.lower().split()
                confirm = any(word in user_input_to_check for word in yesses)
                deny = any(word in user_input_to_check for word in nopes)

                if confirm:
                    response = conversation_manager.process_confirmation(True)
                    # print(response)
                    dialog_response(response)

                    # Add this: Immediately ask the next question after confirmation
                    missing_info = conversation_manager.check_missing_info()
                    if missing_info:
                        next_question = assistant.generate_response(missing_info[0])
                        dialog_response(next_question)
                    else:
                        print('ASSISTANT: I believe I have all information now')
                        print(conversation_manager.return_details())
                        conversation_active = False

                    continue
                elif deny:
                    response = conversation_manager.process_confirmation(False)
                    dialog_response(response)
                    continue

            # Handle intents only if not in confirmation mode
            elif intent == 'farewell':
                response = assistant.generate_response('farewell')
                dialog_response(response)
                conversation_active = False
                break
            elif intent == 'fallback':
                response = assistant.generate_response('fallback')
                dialog_response(response)
                continue
            elif intent == 'greetings':
                response = assistant.generate_response('greetings')
                dialog_response(response)
                continue

            # Check missing info and ask
            missing_info = conversation_manager.check_missing_info()
            # print(f'DEBUG Missing info: {missing_info}')

            if missing_info:
                response = assistant.generate_response(missing_info[0])
                conversation_manager.last_question = missing_info[0]
                dialog_response(response)
            else:
                print('ASSISTANT: I believe I have all information now')
                print(conversation_manager.return_details())
                conversation_active = False

        except Exception as e:
            print(f'ERROR:{type(e)}, {e}')
            response = f'ASSISTANT: I am sorry, there was a problem while processing your request. Please try again.'
            dialog_response(response)


    print('ASSISTANT: Please wait while I prepare the list of restaurants.')

    # Get all user's details
    details = conversation_manager.return_details()
    user_preferences = [details['booking_location'], details['dietary_preferences'], details['culinary_preferences']]

    # Create a query based on user's preferences
    restaurants = find_restaurants(
        diet=details['dietary_preferences'],
        cuisine=details['culinary_preferences'],
        city='Warsaw',
        area=details['booking_location'],
    )

    suggestions = assistant.generate_restaurant_suggestion(restaurants, user_preferences)


    for suggestion in suggestions:
        print('Restaurant: ', suggestion['restaurant_name'])
        print('Address: ', suggestion['restaurant_address'])
        print('Rating: ', suggestion['rating'])
        print('Summary: ', suggestion['summary'])


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