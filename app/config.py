"""Configuration settings for the OCR system."""

# Supported languages
LANGUAGES = {
    'en': 'eng',  # English
    'ar': 'ara'   # Arabic
}

# Document types
DOCUMENT_TYPES = {
    'ID_CARD': 'id_card',
    'REPORT': 'report'
}

# ID card types
ID_CARD_TYPES = {
    'TYPE_1': 'type_1',
    'TYPE_2': 'type_2',
    'TYPE_3': 'type_3'
}

# Report types
REPORT_TYPES = {
    'TYPE_1': 'report_1',
    'TYPE_2': 'report_2',
    'TYPE_3': 'report_3'
}

# Field coordinates for different document types
# Format: (x1, y1, x2, y2) - normalized coordinates
FIELD_COORDINATES = {
    'ID_CARD': {
        'TYPE_1': {
            'front': {
                'name': (0.1, 0.2, 0.6, 0.3),
                'id_number': (0.1, 0.4, 0.4, 0.5),
                # Add more fields as needed
            },
            'back': {
                'address': (0.1, 0.2, 0.8, 0.4),
                # Add more fields as needed
            }
        },
        # Add more ID card types
    },
    'REPORT': {
        'TYPE_1': {
            'header': (0.1, 0.05, 0.9, 0.15),
            'party_1': (0.1, 0.2, 0.9, 0.4),
            'party_2': (0.1, 0.5, 0.9, 0.7),
            # Add more fields as needed
        },
        # Add more report types
    }
}