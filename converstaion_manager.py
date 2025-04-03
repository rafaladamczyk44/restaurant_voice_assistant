

class ConversationManager:
    def __init__(self):
        self.user_name = None
        self.dietary_preferences = None
        self.culinary_preferences = None
        self.party_size = None
        self.booking_date_time = None
        self.previous_intent = None

    def extract_info(self, extracted_info):
        if 'name' in extracted_info:
            self.user_name = extracted_info['name']
        if 'dietary_preferences' in extracted_info:
            self.dietary_preferences = extracted_info['dietary_preferences']
        if 'culinary_preferences' in extracted_info:
            self.culinary_preferences = extracted_info['culinary_preferences']
        if 'party_size' in extracted_info:
            self.party_size = extracted_info['party_size']
        if 'booking_date_time' in extracted_info:
            self.booking_date_time = extracted_info['booking_date_time']

    def check_missing_info(self):
        missing_info = []
        if not self.user_name:
            missing_info.append("ask_name")
        if not self.dietary_preferences:
            missing_info.append("get_dietary_preferences")
        if not self.culinary_preferences:
            missing_info.append("get_cuisine_preferences")
        if not self.party_size:
            missing_info.append("get_party_size")
        if not self.booking_date_time:
            missing_info.append("get_date_time")

        return missing_info