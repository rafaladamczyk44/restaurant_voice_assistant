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
               - "name": user's name if mentioned
               - "dietary": dietary preferences/restrictions if mentioned
               - "cuisine": cuisine preference if mentioned
               - "time": booking time/date if mentioned
               - "guest_count": number of guests if mentioned
               
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

    def recognize_entity(self, query:str):
        """
        Function for recognizing named entities from user's input
        :param query: Transcript from audio
        :return:
        """

    def generate_response(self, intent, intents_list):
        """
        Based on the recognized intent, return one of the responses
        :param intent: Intent to generate the reply for
        :param intents_list: Intents list
        :return: Response for the intent
        """
        pool_of_responses = intents_list[intent]['responses']
        return pool_of_responses[random.randint(0, 2)]