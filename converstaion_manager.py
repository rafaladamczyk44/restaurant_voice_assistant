class ConversationManager:
    def __init__(self):
        self.user_name = None
        self.dietary_preferences = None
        self.culinary_preferences = None
        self.party_size = None
        self.booking_date_time = None
        self.booking_location = None

        # For state tracking
        self.current_state = 'greetings'
        self.last_question = None
        self.history = []

    def update_state(self, new_state):
        """Switch to new state, update the history"""
        self.history.append((self.current_state, new_state))
        self.current_state = new_state

    def add_user_history(self, query):
        self.history.append({'role': 'user',
                             'query': query,})

    def add_sys_history(self, query):
        self.history.append({'role': 'system',
                             'query': query,})

    def extract_info(self, extracted_info: dict):
        """
        Extract information from extracted_info from user query
        :param extracted_info: Dictionary with extracted information from the query
        """
        if 'name' in extracted_info and extracted_info['name']:
            self.user_name = extracted_info['name']

        if 'dietary_preferences' in extracted_info and extracted_info['dietary_preferences']:
            self.dietary_preferences = extracted_info['dietary_preferences']

        if 'culinary_preferences' in extracted_info and extracted_info['culinary_preferences']:
            self.culinary_preferences = extracted_info['culinary_preferences']

        if 'party_size' in extracted_info and extracted_info['party_size']:
            self.party_size = extracted_info['party_size']

        if 'booking_date_time' in extracted_info and extracted_info['booking_date_time']:
            self.booking_date_time = extracted_info['booking_date_time']

        if 'booking_location' in extracted_info and extracted_info['booking_location']:
            self.booking_location = extracted_info['booking_location']

    def check_missing_info(self) -> list:
        """
        Check the current missing info, direct the conversation accordingly
        :return: List of missing info
        """
        missing_info = []
        if not self.user_name:
            missing_info.append("ask_name")
        if not self.dietary_preferences:
            # TODO: Allow for none
            missing_info.append("get_dietary_preferences")
        if not self.culinary_preferences:
            missing_info.append("get_cuisine_preferences")
        if not self.party_size:
            # TODO: get the number restrictions (0 to 9?)
            missing_info.append("get_party_size")
        if not self.booking_date_time:
            missing_info.append("get_date_time")
        if not self.booking_location:
            missing_info.append("get_location")
        return missing_info

    def return_history(self) -> list:
        """Return full history of conversation intent based"""
        return self.history

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