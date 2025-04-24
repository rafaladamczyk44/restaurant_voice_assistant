import os
import random
import json
from openai import OpenAI

# https://platform.openai.com/docs/api-reference/chat/create
API_KEY = os.environ.get('OPENAI_KEY')

class Assistant:
    def __init__(self, intents, intent_categories, model="gpt-4o-mini"):
        self.client = OpenAI(api_key=API_KEY)
        self.model = model
        self.intents = intents
        self.intent_categories = intent_categories

        self.last_question_type = None

    def recognize_answer_type(self, query):
        """
        Recognize if what user said is confirmation (Yes) or (No)
        :param query: User input
        :return: Bool
        """
        assert query is not None
        prompt = f"""
            Your task is to recognize if the sentence means "YES" or "NO".
            For example:
            "yes, sure", "yeah", "its correct" - it is "YES"
            "no", "wrong", "no sorry" - it is "NO"
            
            If the processed query is a "YES", return True, if it is "NO", return False
            
            User query: {query}
            
            JSON response: 
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content)

        return result['response']

    def recognize_intent(self, query: str, last_question_type=None):
        """
        Method to recognize the intent from user's input
        :param query: Transcript from audio
        :param last_question_type: what was asked last
        :return: Recognized intent + Extracted extra info
        """
        assert query is not None, 'Empty query provided'
        assert len(self.intent_categories) > 0, 'Intents list empty'

        # Store the last question type for context
        if last_question_type:
            self.last_question_type = last_question_type

        # context-aware prompt
        context_instruction = ""
        if self.last_question_type == "get_dietary_preferences":
            context_instruction = """
                    The last question asked to the user was about dietary preferences.
                    If the user responds with just "No", "None", "Nope", "Not really", or any simple negative response, 
                    interpret this as having NO dietary preferences and set "dietary_preferences" to "NO_PREFERENCE".
                    """
        elif self.last_question_type == "get_cuisine_preferences":
            context_instruction = """
                    The last question asked to the user was about cuisine preferences.
                    If the user responds with just "No", "None", "Nope", "Not really", "Anything", or any simple negative response,
                    interpret this as having NO cuisine preferences and set "culinary_preferences" to "NO_PREFERENCE".
                    """
        
        prompt = f"""
            You are an intent recognition system for a restaurant booking voice assistant.
            Based on the user's input, identify the most appropriate intent category from the following options:
            {', '.join(self.intent_categories)}

            {context_instruction}
             
            User input: "{query}"

            Respond with a JSON object containing:
            1. "intent": the most appropriate intent category
            2. "confidence": your confidence score (0-1)
            3. "extracted_info": a dictionary with any relevant information extracted from the input, with keys including:
               - "name": user's first name 
               - "dietary_preferences": dietary preferences/restrictions if mentioned or None. 
               If the user explicitly states they have no preferences or restrictions (e.g., "no dietary restrictions", 
               "I eat everything", "no preferences", etc.), set this to "NO_PREFERENCE". 
               If not mentioned, set to empty string.
               - "culinary_preferences": cuisine preference if mentioned or None. 
               If the user explicitly states they have no cuisine preference (e.g., "any cuisine", "I like all food", 
               "no preference", etc.), set this to "NO_PREFERENCE". 
               If not mentioned, set to empty string.
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

        return response_clean['intent'], response_clean['extracted_info'], response_clean['confidence']

    def generate_response(self, intent):
        """
        Based on the recognized intent, return one of the responses
        :param intent: Intent to generate the reply for
        :return: Response for the intent
        """
        assert intent in self.intents, 'Intent not in the list'
        assert len(self.intents) > 0, 'Intent list is empty'

        self.last_question_type = intent

        pool_of_responses = self.intents[intent]['responses']
        return pool_of_responses[random.randint(0, 2)]

    def generate_api_query(self, user_details):
        prompt = f'''Your task is to preapre an API query based on user details.
        User your language skills to extract data from a Python dictionary and prepare a robust Google search query.
        For example, based on user details:
            Vegan restaurant in the city Center Warsaw,
            Best italian restaurant in the downtown, Warsaw,
            Georgian restaurant for two in Warsaw
            
        User booking details: 
        {user_details}
        
        Return a simple string.
        Response:
        '''
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "text"}
        )
        # print(response.choices[0].message.content)
        return response.choices[0].message.content

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
        print(result)

        if result:
            try:
                result = result['top_picks']
            except KeyError: # If only one restaurant is returned
                print('Only one restaurant found')
            finally:
                return result
        else:
            print("SYSTEM: Couldn't find any restaurant")
            return None