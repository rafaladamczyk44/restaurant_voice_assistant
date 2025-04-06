

class ConversationManager:
    def __init__(self):
        self.user_name = None
        self.dietary_preferences = None
        self.culinary_preferences = None
        self.party_size = None
        self.booking_date_time = None
        self.previous_intent = None
        self.recommended_restaurant = None

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

    def adapt_extracted_info(self, info):
        adapted_info = {}
        if 'name' in info and info['name']:
            adapted_info['name'] = info['name']
        if 'dietary' in info and info['dietary']:
            adapted_info['dietary_preferences'] = info['dietary']
        if 'cuisine' in info and info['cuisine']:
            adapted_info['culinary_preferences'] = info['cuisine']
        if 'time' in info and info['time']:
            adapted_info['booking_date_time'] = info['time']
        if 'guest_count' in info and info['guest_count']:
            adapted_info['party_size'] = info['guest_count']
        return adapted_info

    def fill_template(self, response):
        filled_response = response
        if "{name}" in filled_response and self.user_name:
            filled_response = filled_response.replace("{name}", self.user_name)
        if "{cuisine}" in filled_response and self.culinary_preferences:
            filled_response = filled_response.replace("{cuisine}", self.culinary_preferences)
        if "{dietary}" in filled_response and self.dietary_preferences:
            filled_response = filled_response.replace("{dietary}", self.dietary_preferences)
        if "{party_size}" in filled_response and self.party_size:
            filled_response = filled_response.replace("{party_size}", str(self.party_size))
        if "{date_time}" in filled_response and self.booking_date_time:
            filled_response = filled_response.replace("{date_time}", self.booking_date_time)
        if self.recommended_restaurant and "{restaurant_name}" in filled_response:
            filled_response = filled_response.replace("{restaurant_name}", self.recommended_restaurant["name"])

        return filled_response

