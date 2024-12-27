"""Data validation module."""
import re
from datetime import datetime

class DataValidator:
    def __init__(self):
        self.validation_rules = {
            'id_number': r'^\d{10}$',  # Example: 10 digits
            'phone': r'^\+?[\d\s-]{8,}$',
            'email': r'^[\w\.-]+@[\w\.-]+\.\w+$',
            'date': r'^\d{2}/\d{2}/\d{4}$'
        }
    
    def validate_field(self, field_name, value):
        """Validate a field value against predefined rules."""
        if field_name in self.validation_rules:
            pattern = self.validation_rules[field_name]
            return bool(re.match(pattern, value))
        return True
    
    def format_date(self, date_str):
        """Format date string to standard format."""
        try:
            date_obj = datetime.strptime(date_str, '%d/%m/%Y')
            return date_obj.strftime('%Y-%m-%d')
        except ValueError:
            return None
    
    def clean_text(self, text):
        """Clean and normalize text data."""
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Remove special characters if needed
        text = re.sub(r'[^\w\s@.-]', '', text)
        return text.strip()