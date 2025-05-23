import os
import yaml
import requests
import argparse

from speech_to_text import STT
from text_to_speech import TTS
from assistant_nlu import Assistant
from converstaion_manager import ConversationManager

GOOGLE_API_KEY = os.getenv('GOOGLE_KEY')

def parse_args():
    parser = argparse.ArgumentParser(description='Voice Assistant for Restaurant Booking')
    parser.add_argument('--no-debug', dest='debug', action='store_false',
                        help='Disable debug mode (debug is enabled by default)')

    parser.set_defaults(debug=True)
    return parser.parse_args()


def find_restaurants(query) -> list:

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
    else:
        tts.generate_audio(response)


def main():
    # Greeting to the user opening the app
    greetings_response = assistant.generate_response('greetings')
    dialog_response(greetings_response)

    # "global" varaibles for the dialog
    past_bookings = False
    conversation_active = True

    # MAIN dialog loop
    while conversation_active:
        try:
            # User input
            if DEBUG:
                user_query = input('User: ')
            else:
                print('Listening for user input...')
                user_query = stt.record_audio()
                print(f'USER: {user_query}')

            # Ask if first time using app
            # If yes, ask if want to use the past recommendation
                # If yes jump straight to previous data
            # If no continue
            if not conversation_manager.first_time_user_confiramtion:
                dialog_response('Is this the first time you are using this application?')

                if DEBUG:
                    first_time_reply = input('User: ')
                else:
                    first_time_reply = stt.record_audio()

                if not assistant.recognize_answer_type(first_time_reply):
                    conversation_manager.first_time_user_confiramtion = False

                    dialog_response('Would you like to use your previous recommendation?')

                    if DEBUG:
                        reply = input('User: ')
                    else:
                        reply = stt.record_audio()

                    if assistant.recognize_answer_type(reply):
                        past_bookings = True
                        conversation_active = False
                else:
                    conversation_manager.first_time_user_confiramtion = True

            # keep track of the last asked question (for cuisine and diet)
            last_question = conversation_manager.last_question

            # Extracting information from user's input
            intent, extracted_info, confidence = assistant.recognize_intent(user_query, last_question)

            # We fill the slot and then pass them for confirmation
            # extract_info -> confirm_field
            confirmation_prompt = conversation_manager.extract_info(extracted_info)
            if confirmation_prompt:
                dialog_response(confirmation_prompt)
                continue

            # Check if we're in confirmation mode first
            if conversation_manager.current_confirm_field:
                confirmed = assistant.recognize_answer_type(user_query)

                if confirmed: # If user said yes
                    response = conversation_manager.process_confirmation(True)

                    # Add correct recognition
                    conversation_manager.positive_responses += 1

                    # print(response)
                    dialog_response(response)
                    missing_info = conversation_manager.check_missing_info()

                    if missing_info:
                        next_question = assistant.generate_response(missing_info[0])
                        dialog_response(next_question)
                    else:
                        print('ASSISTANT: I believe I have all information now')
                        # print(conversation_manager.return_details())
                        conversation_active = False
                        conversation_manager.save_user_data()
                    continue

                else: # if user said "no"
                    response = conversation_manager.process_confirmation(False)

                    # Add wrong
                    conversation_manager.negative_responses += 1

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
                # print(conversation_manager.return_details())
                conversation_active = False
                conversation_manager.save_user_data()

        except Exception as e:
            print(f'ERROR:{type(e)}, {e}')
            response = f'ASSISTANT: I am sorry, there was a problem while processing your request. Please try again.'
            dialog_response(response)


    dialog_response('ASSISTANT: Please wait while I prepare the list of restaurants.')

    # Get all user's details
    details = {}
    user_preferences = []

    if not past_bookings:
        details = conversation_manager.return_details()
        user_preferences = [details['booking_location'], details['dietary_preferences'], details['culinary_preferences']]
    else:
        # TODO: Add part where we search in the past data
        pass

    # Based on user preferences, create query for Google search
    api_query = assistant.generate_api_query(details)

    # Create a query based on user's preferences
    restaurants = find_restaurants(api_query)

    # Based on the results prepare restaurant suggestions
    suggestions = assistant.generate_restaurant_suggestion(restaurants, user_preferences)

    if not suggestions:
        print('ASSISTANT: Sorry, I did not find any suggestions.')
        return

    for idx, suggestion in enumerate(suggestions):
        print(suggestion)

        restaurant_suggestion = f"""
        Based on your preferences, I would like to suggest a booking in {suggestion['restaurant_name']} - a restaurant wit {suggestion['rating']} rating.
        The restaurant's address is {suggestion['address']}.
        {suggestion['summary']}        
        """

        dialog_response(restaurant_suggestion)

        if DEBUG:
            user_response = input('User (yes/no): ')
        else:
            print('Listening for confirmation...')
            user_response = stt.record_audio()
            print(f'USER: {user_response}')

        # Check if user confirms this suggestion
        # yesses = ['yes', 'yeah', 'sure', 'ok', 'okay', 'book it', 'sounds good', 'perfect']
        # nopes = ['no', 'nope', 'next', 'another', 'different', 'something else', 'pass']

        confirmed = assistant.recognize_answer_type(user_response)

        if confirmed:
            # User confirmed this suggestion, complete the booking
            booking_confirmation = f"Great! I've booked a table for {details['party_size']} at {suggestion['restaurant_name']} "
            booking_confirmation += f"for {details['booking_date_time']}. You'll receive a confirmation shortly. "
            booking_confirmation += "Thank you for using our restaurant booking service!"

            dialog_response(booking_confirmation)
            return  # end here

        else:
            # User rejected this suggestion
            if idx < len(suggestions) - 1:
                dialog_response("Let me suggest another restaurant for you.")
            else:
                # This was the last suggestion
                dialog_response(
                    "I'm sorry, I've run out of suggestions that match your preferences. Would you like to try with different criteria?")
                return

    # for suggestion in suggestions:
    #     print('Restaurant: ', suggestion['restaurant_name'])
    #     print('Address: ', suggestion['restaurant_address'])
    #     print('Rating: ', suggestion['rating'])
    #     print('Summary: ', suggestion['summary'])

if __name__ == '__main__':
    # For testing so I don't have to speak everytime
    # DEBUG = True

    args = parse_args()
    DEBUG = args.debug

    DEBUG = False

    with open('intents.yaml', 'r') as file:
        intents = yaml.safe_load(file)

    intents_categories = list(intents.keys())

    # Initialize all my classes
    stt = STT()
    tts = TTS()
    assistant = Assistant(intents=intents, intent_categories=intents_categories)
    conversation_manager = ConversationManager()


    # deets = {
    #         'user_name': 'Rafal',
    #         'booking_time': 'Today',
    #         'booking_location': 'Warsaw Center',
    #         'party_size': 4,
    #         'dietary_preferences': 'None',
    #         'culinary_preferences': 'Italian',
    #     }
    # assistant.generate_api_query(deets)


    # Initialize the app

    main()