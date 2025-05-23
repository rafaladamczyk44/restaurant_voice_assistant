import os
import sqlite3
import hashlib
from datetime import datetime

class ConversationManager:
    def __init__(self):
        # User details
        self.user_name = None
        self.dietary_preferences = None
        self.culinary_preferences = None
        self.party_size = None
        self.booking_date_time = None
        self.booking_location = None

        # Tracking last question for assistant nlu recognize_intent method (context about preferences)
        self.last_question = None

        self.first_time_user_confiramtion = None

        # Fields tracking
        self.current_confirm_field = None  # current field
        self.confirmed_fields = set() # already confirmed fields
        self.no_preference_fields = set() # fields with No as preference, ex. diet

        # For evaluation
        self.positive_responses = 0
        self.negative_responses = 0

    def extract_info(self, extracted_info: dict):
        """
        Extract information from extracted_info from user query
        :param extracted_info: Dictionary with extracted information from the query
        """
        newly_added = []

        if 'name' in extracted_info and extracted_info['name']:
            self.user_name = extracted_info['name']
            newly_added.append('name')

        if 'dietary_preferences' in extracted_info:
            if extracted_info['dietary_preferences'] == "NO_PREFERENCE":
                self.dietary_preferences = "No specific dietary preferences"
                self.no_preference_fields.add('dietary_preferences')
                newly_added.append('dietary_preferences')
            elif extracted_info['dietary_preferences']:
                self.dietary_preferences = extracted_info['dietary_preferences']
                newly_added.append('dietary_preferences')

        if 'culinary_preferences' in extracted_info:
            if extracted_info['culinary_preferences'] == "NO_PREFERENCE":
                self.culinary_preferences = "No specific cuisine preferences"
                self.no_preference_fields.add('culinary_preferences')
                newly_added.append('culinary_preferences')
            elif extracted_info['culinary_preferences']:
                self.culinary_preferences = extracted_info['culinary_preferences']
                newly_added.append('culinary_preferences')

        if 'party_size' in extracted_info and extracted_info['party_size']:
            self.party_size = extracted_info['party_size']
            newly_added.append('party_size')

        if 'booking_date_time' in extracted_info and extracted_info['booking_date_time']:
            self.booking_date_time = extracted_info['booking_date_time']
            newly_added.append('booking_date_time')

        if 'booking_location' in extracted_info and extracted_info['booking_location']:
            self.booking_location = extracted_info['booking_location']
            newly_added.append('booking_location')

        if newly_added and not self.current_confirm_field:
            # print(f'Newly added: {newly_added[0]}')
            return self.confirm_field(newly_added[0])

        return None

    def confirm_field(self, field):
        """
        Confirm information with user
        :param field:
        :return:
        """

        self.current_confirm_field = field

        if field == 'name':
            return f'To confirm - your name is  {self.user_name.title()}, correct?'
        if field == 'dietary_preferences':
            return f'Your diet preferences are {self.dietary_preferences}, is that right?'
        if field == 'culinary_preferences':
            return f'The cuisine you are hungry for today is {self.culinary_preferences}, is that right?'
        if field == 'party_size':
            if self.party_size > 2:
                return f'If I understood correctly, this will be a {self.party_size} people reservation?'
            if self.party_size == 2:
                return f'So that will be a table for two, right?'
            if self.party_size == 1:
                return f'One person reservation, correct?'
        if field == 'booking_date_time':
            return f'Just to confirm, your reservation will be asked for {self.booking_date_time}'
        if field == 'booking_location':
            return f'Place you want to book is in {self.booking_location}, correct?'

    def process_confirmation(self, confirmation):
        field = self.current_confirm_field
        if confirmation:
            self.confirmed_fields.add(field) # add to set of already confirmed
            self.current_confirm_field = None # zero the current state
            return f'Thanks, {field} has been confirmed'
        else:
            self.current_confirm_field = None
            setattr(self, field, None)
            # If in no preference, remove
            if field in self.no_preference_fields:
                self.no_preference_fields.remove(field)
            return f'Would you kindly provde your {self.current_confirm_field} again, please?'

    def check_missing_info(self) -> list:
        """
        Check the current missing info, direct the conversation accordingly
        :return: List of missing info
        """
        missing_info = []
        if not self.user_name:
            missing_info.append("ask_name")
        if not self.dietary_preferences and 'dietary_preferences' not in self.no_preference_fields:
            missing_info.append("get_dietary_preferences")
        if not self.culinary_preferences and 'culinary_preferences' not in self.no_preference_fields:
            missing_info.append("get_cuisine_preferences")
        if not self.party_size:
            missing_info.append("get_party_size")
        if not self.booking_date_time:
            missing_info.append("get_date_time")
        if not self.booking_location:
            missing_info.append("get_location")

        if missing_info:
            self.last_question = missing_info[0]

        return missing_info

    def return_details(self) -> dict:
        """Return booking details"""
        return {
            'user_name': self.user_name,
            'booking_time': self.booking_date_time,
            'booking_location': self.booking_location,
            'party_size': self.party_size,
            'dietary_preferences': self.dietary_preferences,
            'culinary_preferences': self.culinary_preferences,
        }

    def save_user_data(self):
        assert self.user_name is not None, 'SYSTEM: No user name'

        data = self.return_details()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Hashmap for user's name storing
        hashed_name = hashlib.sha256(self.user_name.encode()).hexdigest()
        data['user_name'] = hashed_name

        # Creates user_data directory if doesnt exist
        os.makedirs("user_data", exist_ok=True)

        db_path = f"user_data/{timestamp}-{hashed_name}.sqlite"

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Create table
            cursor.execute('''
                CREATE TABLE user_booking_data (
                    user_name TEXT,
                    dietary_preferences TEXT,
                    culinary_preferences TEXT,
                    party_size INTEGER,
                    booking_date_time TEXT,
                    booking_location TEXT,
                    accuracy_evaluation FLOAT
                )
                ''')

            # Insert data
            cursor.execute('''
                    INSERT INTO user_booking_data VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                data['user_name'],
                data['booking_time'],
                data['booking_location'],
                data['party_size'],
                data['dietary_preferences'],
                data['culinary_preferences'],
                self.return_evaluation_accuracy()
            ))

            conn.commit()
            conn.close()
            print(f"Data saved to {db_path}")
        except Exception as e:
            print(f"Error saving data: {e}")

    def return_evaluation_accuracy(self):
        """
        Return assistant's accuracy (all correct / all responses)
        :return: accuracy: float
        """
        if (self.positive_responses + self.negative_responses) == 0:
            return None

        return self.positive_responses / (self.positive_responses + self.negative_responses)