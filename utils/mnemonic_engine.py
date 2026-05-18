"""
Z32 Nexus - Mnemonic Engine
Feature 7: Memory tricks and associations for vocabulary learning

Generates and manages mnemonic devices to help memorize vocabulary:
- Sound-alike associations (palabra sounds like "pull a bra")
- Visual imagery suggestions
- Story-based memory techniques
- Keyword method connections
"""

import logging
import random
from typing import Optional, List, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


# Common English words that sound like Spanish words for keyword method
SOUND_ALIKES = {
    # Spanish: (English sound-alike, memory image)
    'casa': ('casa sounds like "case-a"', 'Imagine a CASE full of houses'),
    'libro': ('libro sounds like "lee-bro"', 'Your BRO is READING (lee) a book'),
    'agua': ('agua sounds like "agua"', 'An IGUANA drinking water'),
    'comer': ('comer sounds like "come here"', 'Come here to EAT'),
    'dormir': ('dormir sounds like "door mirror"', 'A mirror on your bedroom DOOR for sleeping'),
    'hablar': ('hablar sounds like "a-blar"', 'You BLUR when you talk too fast'),
    'perro': ('perro sounds like "pair-o"', 'A PAIR OF dogs'),
    'gato': ('gato sounds like "got-oh"', 'GOT a cat? Oh!'),
    'trabajo': ('trabajo sounds like "trabaho"', 'TROUBLE at WORK'),
    'dinero': ('dinero sounds like "dine-arrow"', 'An ARROW pointing to where you DINE needs money'),
    'tiempo': ('tiempo sounds like "tempo"', 'The TEMPO of time'),
    'grande': ('grande sounds like "grand"', 'Something GRAND is big'),
    'pequeño': ('pequeño sounds like "peck-enyoh"', 'A small bird PECKs'),
    'amigo': ('amigo sounds like "a-me-go"', 'A friend says "Let ME GO with you"'),
    'bueno': ('bueno sounds like "bway-no"', 'NO WAY its not good!'),
    'malo': ('malo sounds like "mah-lo"', 'MA always says LO and behold when bad things happen'),
    'mujer': ('mujer sounds like "moo-hair"', 'A WOMAN with hair that MOOs'),
    'hombre': ('hombre sounds like "hom-bray"', 'A MAN wearing a SOMBRERO'),
    'niño': ('niño sounds like "neen-yo"', 'A little CHILD eating a NINO cookie'),
    'ciudad': ('ciudad sounds like "see-you-dad"', 'SEE YOU DAD in the CITY'),
    'calle': ('calle sounds like "call-yay"', 'CALL someone on the STREET'),
    'tienda': ('tienda sounds like "tea-end-ah"', 'At the END of the STORE they serve TEA'),
    'escuela': ('escuela sounds like "eskwela"', 'SQUEALING kids at SCHOOL'),
    'médico': ('médico sounds like "medic-oh"', 'A MEDIC is a DOCTOR'),
    'enfermo': ('enfermo sounds like "in-firm-oh"', 'IN a FIRM bed when SICK'),
    'feliz': ('feliz sounds like "feel-ease"', 'You FEEL at EASE when HAPPY'),
    'triste': ('triste sounds like "tree-stay"', 'A SAD tree that has to STAY'),
    'cansado': ('cansado sounds like "can-sad-oh"', 'You CAN be SAD when TIRED'),
    'hambre': ('hambre sounds like "ham-bray"', 'Wanting HAM when HUNGRY'),
    'sed': ('sed sounds like "said"', 'He SAID he was THIRSTY'),
}


# Visual imagery templates for different word types
VISUAL_TEMPLATES = {
    'noun': [
        "Picture a giant {spanish} in your living room",
        "Imagine {english} dancing with the letters {spanish}",
        "See yourself holding a {english} with '{spanish}' written on it",
        "Visualize a {english} made of the letters {spanish}",
    ],
    'verb': [
        "Picture yourself {english}ing while saying '{spanish}'",
        "Imagine someone famous {english}ing and shouting '{spanish}'",
        "See a cartoon character {english}ing with '{spanish}' floating above",
    ],
    'adjective': [
        "Imagine something {english} glowing with the word '{spanish}'",
        "Picture the most {english} thing covered in '{spanish}' letters",
        "See yourself touching something {english} labeled '{spanish}'",
    ],
}


# Story-based templates
STORY_TEMPLATES = [
    "Once upon a time, a {english} called '{spanish}' went on an adventure...",
    "In a magical land, everything {english} was known as '{spanish}'...",
    "The famous wizard named their {english} pet '{spanish}'...",
    "Legend says that '{spanish}' means {english} because...",
]


class MnemonicEngine:
    """
    Generates mnemonic devices for vocabulary memorization.
    Uses multiple techniques:
    - Keyword method (sound associations)
    - Visual imagery
    - Story-based memory
    - Location/memory palace connections
    """
    
    def __init__(self):
        self._sound_alikes = SOUND_ALIKES
    
    def generate_mnemonic(self, spanish: str, english: str, 
                          part_of_speech: str = 'noun') -> dict:
        """
        Generate a complete mnemonic package for a word.
        
        Returns:
            dict with keys: sound_association, visual_image, story, keywords
        """
        result = {
            'spanish': spanish,
            'english': english,
            'sound_association': self._get_sound_association(spanish),
            'visual_image': self._get_visual_image(spanish, english, part_of_speech),
            'story': self._get_story(spanish, english),
            'keywords': self._extract_keywords(spanish, english),
            'effectiveness_tips': self._get_memorization_tips(),
        }
        
        return result
    
    def _get_sound_association(self, spanish: str) -> Tuple[str, str]:
        """Get sound-alike association if available."""
        spanish_lower = spanish.lower().strip()
        
        if spanish_lower in self._sound_alikes:
            return self._sound_alikes[spanish_lower]
        
        # Generate a basic sound-alike suggestion
        return (
            f"'{spanish}' sounds like '{self._phonetic_approximation(spanish)}'",
            f"Create a vivid image connecting this sound to the meaning"
        )
    
    def _phonetic_approximation(self, spanish: str) -> str:
        """Create an English phonetic approximation of Spanish word."""
        # Basic phonetic rules for Spanish to English approximation
        result = spanish.lower()
        
        # Common Spanish to English sound mappings
        mappings = [
            ('ll', 'y'),
            ('ñ', 'ny'),
            ('rr', 'rr'),
            ('j', 'h'),
            ('h', ''),  # Silent h
            ('qu', 'k'),
            ('gu', 'gw'),
            ('z', 's'),
            ('c', 'k'),  # Before a, o, u
            ('v', 'b'),
        ]
        
        for old, new in mappings:
            result = result.replace(old, new)
        
        return result
    
    def _get_visual_image(self, spanish: str, english: str, 
                          part_of_speech: str) -> str:
        """Generate a visual imagery suggestion."""
        templates = VISUAL_TEMPLATES.get(part_of_speech, VISUAL_TEMPLATES['noun'])
        template = random.choice(templates)
        
        return template.format(spanish=spanish, english=english)
    
    def _get_story(self, spanish: str, english: str) -> str:
        """Generate a mini-story for the word."""
        template = random.choice(STORY_TEMPLATES)
        return template.format(spanish=spanish, english=english)
    
    def _extract_keywords(self, spanish: str, english: str) -> List[str]:
        """Extract memorable keywords from both words."""
        keywords = []
        
        # Add syllables that might trigger memory
        if len(spanish) >= 3:
            keywords.append(spanish[:3])
        if len(spanish) >= 4:
            keywords.append(spanish[-3:])
        
        # Add rhyming possibilities
        keywords.append(f"rhymes with words ending in '-{spanish[-2:]}'")
        
        return keywords
    
    def _get_memorization_tips(self) -> List[str]:
        """Get general tips for better memorization."""
        tips = [
            "Make the image vivid, colorful, and exaggerated",
            "Add movement and action to your mental picture",
            "Include emotions - funny or surprising images stick better",
            "Connect to something personal in your life",
            "Review within 24 hours to solidify the memory",
            "Say the word out loud while visualizing",
            "Draw the mental image if you're visual learner",
        ]
        return random.sample(tips, min(3, len(tips)))
    
    def suggest_memory_palace_location(self, spanish: str, category: str) -> str:
        """
        Suggest a memory palace location based on word category.
        Feature 6: Memory Palace Integration
        """
        locations = {
            'food': ['kitchen counter', 'refrigerator', 'dining table', 'pantry'],
            'house': ['living room', 'bedroom', 'bathroom', 'hallway'],
            'family': ['family photo wall', 'dinner table', 'car backseat'],
            'body': ['bathroom mirror', 'gym', 'doctor office'],
            'nature': ['garden', 'window view', 'balcony', 'park bench'],
            'travel': ['suitcase', 'front door', 'car dashboard', 'airport'],
            'work': ['desk', 'computer screen', 'office door', 'meeting room'],
            'emotions': ['heart', 'mirror', 'pillow', 'diary'],
            'time': ['clock on wall', 'calendar', 'watch on wrist'],
            'general': ['front door', 'bedside table', 'kitchen sink', 'window'],
        }
        
        category_locations = locations.get(category.lower(), locations['general'])
        location = random.choice(category_locations)
        
        return f"Place '{spanish}' in your {location}"
    
    def get_cognate_hint(self, spanish: str, english: str) -> Optional[str]:
        """
        Detect if words are cognates and provide a hint.
        Feature 44: Cognate Detection
        """
        spanish_lower = spanish.lower()
        english_lower = english.lower()
        
        # Check for exact match (rare but possible)
        if spanish_lower == english_lower:
            return f"Perfect cognate! '{spanish}' is spelled the same in both languages."
        
        # Check for common cognate patterns
        cognate_patterns = [
            # Spanish ending -> English ending
            ('ción', 'tion'),  # información -> information
            ('dad', 'ty'),      # universidad -> university
            ('mente', 'ly'),    # exactamente -> exactly
            ('oso', 'ous'),     # famoso -> famous
            ('ivo', 'ive'),     # activo -> active
            ('al', 'al'),       # natural -> natural
            ('ble', 'ble'),     # posible -> possible
            ('ismo', 'ism'),    # turismo -> tourism
            ('ista', 'ist'),    # artista -> artist
        ]
        
        for spanish_end, english_end in cognate_patterns:
            if spanish_lower.endswith(spanish_end) and english_lower.endswith(english_end):
                root_spanish = spanish_lower[:-len(spanish_end)]
                root_english = english_lower[:-len(english_end)]
                
                if root_spanish[:3] == root_english[:3]:  # Similar roots
                    return (f"Cognate pattern: Spanish -{spanish_end} = English -{english_end}. "
                           f"Root '{root_spanish}' is similar in both languages!")
        
        # Check for high similarity (>70% character match)
        matches = sum(1 for a, b in zip(spanish_lower, english_lower) if a == b)
        similarity = matches / max(len(spanish_lower), len(english_lower))
        
        if similarity > 0.7:
            return f"Near cognate! '{spanish}' and '{english}' share {int(similarity*100)}% of letters."
        
        return None


# Singleton instance
mnemonic_engine = MnemonicEngine()
