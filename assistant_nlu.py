import os
import random
import json
from openai import OpenAI

API_KEY = os.environ.get('OPENAI_KEY')

class Assistant:
    def __init__(self, intents, intent_categories, model="gpt-4o-mini"):
        self.client = OpenAI(api_key=API_KEY)
        self.model = model
        self.intents = intents
        self.intent_categories = intent_categories

    def recognize_intent(self, query: str):
        """
        Method to recognize the intent from user's input
        :param query: Transcript from audio
        :return: Recognized intent + Extracted extra info
        """
        assert query is not None, 'Empty query provided'
        assert len(self.intent_categories) > 0, 'Intents list empty'

        prompt = f"""
            You are an intent recognition system for a restaurant booking voice assistant.
            Based on the user's input, identify the most appropriate intent category from the following options:
            {', '.join(self.intent_categories)}

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
               
            The answer must have confidence over 0.9. 
            Otherwise, return recognized intent as "fallback"  
               
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
        assert query is not None, 'Empty query provided'

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
            print("Warning: 'entities' key not found in response. Return empty list.")
            print(f"Response received: {response_clean}")
            return []

    def generate_response(self, intent):
        """
        Based on the recognized intent, return one of the responses
        :param intent: Intent to generate the reply for
        :return: Response for the intent
        """
        assert intent in self.intents, 'Intent not in the list'
        assert len(self.intents) > 0, 'Intent list is empty'

        pool_of_responses = self.intents[intent]['responses']
        return pool_of_responses[random.randint(0, 2)]

    def generate_restaurant_suggestion(self, restaurants_list:list, user_preferences:list):
        assert restaurants_list, 'Empty restaurants_list provided'
        assert user_preferences, 'Empty user_preferences provided'

        prompt = f"""   
        You are a helpful culinary advisor. Your goal is to select the best option based on the user input from the restaurant lists.
        You will choose top three picks from a list based on:
        - How close the recent review match the user input.
        - Rating
        For example: if the user requested vegan restaurant and you have to choose from 2 restaurants: 
        - one with rating 4.8, where no one says anything about vegan options 
        - the other restaurant with rating 4.7 but people say things like "great vegan options", "good for vegans"
        You should choose the second restaurant.
        
        Restaurant list: {restaurants_list}
        User preferences: {user_preferences}
        
        Respond with a JSON object containing:
        - restaurant_name
        - restaurant address
        - rating
        - summary of comparison between user needs and restaurant description (good for vegans, great Italian food, etc.)
        
        JSON Response:
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

        return result['top_picks']