import os
import random
import json
from openai import OpenAI

API_KEY = os.environ.get('OPENAI_KEY')

class Assistant:
    def __init__(self, model="gpt-4o-mini"):
        self.client = OpenAI(api_key=API_KEY)
        self.model = model

    def recognize_intent(self, query: str, available_categories:list):
        """
        Method to recognize the intent from user's input
        :param query: Transcript from audio
        :param available_categories: List of available intent categories
        :return: Recognized intent + Extracted extra info
        """

        prompt = f"""
            You are an intent recognition system for a restaurant booking voice assistant.
            Based on the user's input, identify the most appropriate intent category from the following options:
            {', '.join(available_categories)}

            User input: "{query}"

            Respond with a JSON object containing:
            1. "intent": the most appropriate intent category
            2. "confidence": your confidence score (0-1)
            3. "extracted_info": a dictionary with any relevant information extracted from the input, with keys including:
               - "name": user's first name 
               - "dietary_preferences": dietary preferences/restrictions if mentioned or None
               - "culinary_preferences": cuisine preference if mentioned or None
               - "party_size": number of guests if mentioned - always a positive number
               - "booking_date_time": booking time/date if mentioned
               - "booking_location": preferred area of the restaurant
               
               Include empty string values for fields not mentioned in the input.
               
            JSON Response:
            """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        response_clean = json.loads(response.choices[0].message.content)

        return response_clean['intent'], response_clean['extracted_info']

    def recognize_entity(self, query:str) -> list :
        """
        Function for recognizing named entities from user's input
        :param query: Transcript from audio
        :return: Entity, entity's type
        """

        prompt = f"""
        You are an entity recognition system for a restaurant booking voice assistant.
        Based on the provided input, your goal is to identify all named entities.
        The entities you need to look for are: name, city, city area, restaurant name
        
        User input: "{query}"
        
        Respond with a JSON object containing:
        - "entities": a list of objects, where each object contains:
            - "entity" - recognized entity
            - "type" - type of entity
            - "confidence" - your confidence score (0-1)
        
        Return only entities with a confidence over 0.85
        JSON Response:
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )

            response_clean = json.loads(response.choices[0].message.content)

            # Check if 'entities' key exists in the response
            if 'entities' in response_clean:
                return response_clean['entities']
            else:
                # If the model didn't wrap entities in an 'entities' list,
                # it might have returned them directly as a list
                print("Warning: 'entities' key not found in response. Return empty list.")
                print(f"Response received: {response_clean}")
                return []

        except Exception as e:
            print(f"Error in entity recognition: {str(e)}")
            # Return empty list on error to avoid breaking conversation flow
            return []

    def generate_response(self, intent, intents_list):
        """
        Based on the recognized intent, return one of the responses
        :param intent: Intent to generate the reply for
        :param intents_list: Intents list
        :return: Response for the intent
        """
        pool_of_responses = intents_list[intent]['responses']
        return pool_of_responses[random.randint(0, 2)]