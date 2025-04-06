

class ConversationManager:
    def __init__(self):
        self.user_name = None
        self.dietary_preferences = None
        self.culinary_preferences = None
        self.party_size = None
        self.booking_date_time = None
        self.booking_location = None

        # Keep track of last question
        self.last_question = None

    def extract_info(self, extracted_info):
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


    def check_missing_info(self):
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