import os
import yaml
import json
import random

import openai
from openai import OpenAI

from speech_to_text import STT

API_KEY = os.environ.get('OPENAI_KEY')

# stt.record_audio()
stt = STT()
client = OpenAI(api_key=API_KEY)

def recognize_intent(query:str, available_categories):
    prompt = f"""
        You are an intent recognition system for a restaurant booking voice assistant.
        Based on the user's input, identify the most appropriate intent category from the following options:
        {', '.join(available_categories)}

        User input: "{query}"

        Respond with a JSON object containing:
        1. "intent": the most appropriate intent category
        2. "confidence": your confidence score (0-1)
        3. "extracted_info": any relevant information extracted from the input (like cuisine, party size, time, etc.)

        JSON Response:
        """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    response_clean = json.loads(response.choices[0].message.content)

    return response_clean['intent'], response_clean['extracted_info']


def create_response_to_user_intent(intent, intents_list):
    pool_of_responses = intents_list[intent]['responses']
    print(f'Available responses: {pool_of_responses}')
    return pool_of_responses[random.randint(0, 2)]


with open('intents.yaml', 'r') as file:
    intents = yaml.safe_load(file)

intents_categories = list(intents.keys())

while True:
    user_query = stt.record_audio()
    print(f'User said: {user_query}')
    # user_query = 'I want to make a booking for 4 people today'
    try:
        intent_recognized, extra_info = recognize_intent(user_query, intents_categories)
        print(f'Intent recognized: {intent_recognized}')

        response_to_user = create_response_to_user_intent(intent_recognized, intents)
        print(f'SYSTEM: {response_to_user}')
    except Exception as e:
        print('Couldnt recognize the intent :(')


