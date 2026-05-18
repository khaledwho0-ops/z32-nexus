"""
Z32 Nexus - Word Family Expander
Feature 10: Word Family Expansion

Provides related word forms (noun/verb/adjective/adverb) for vocabulary items.
This helps learners understand word derivation patterns and expand vocabulary efficiently.
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


# Common Spanish word family patterns
# Format: root -> {part_of_speech: word_form}
WORD_FAMILIES = {
    # -ar verb families
    'trabaj': {
        'verb_infinitive': ('trabajar', 'to work'),
        'noun_action': ('trabajo', 'work/job'),
        'noun_person': ('trabajador', 'worker'),
        'adjective': ('trabajador', 'hardworking'),
    },
    'habl': {
        'verb_infinitive': ('hablar', 'to speak'),
        'noun_action': ('habla', 'speech'),
        'noun_person': ('hablante', 'speaker'),
        'adjective': ('hablador', 'talkative'),
    },
    'estudi': {
        'verb_infinitive': ('estudiar', 'to study'),
        'noun_action': ('estudio', 'study'),
        'noun_person': ('estudiante', 'student'),
        'adjective': ('estudioso', 'studious'),
    },
    'enseñ': {
        'verb_infinitive': ('enseñar', 'to teach'),
        'noun_action': ('enseñanza', 'teaching'),
        'noun_person': ('enseñante', 'teacher'),
    },
    'cant': {
        'verb_infinitive': ('cantar', 'to sing'),
        'noun_action': ('canto', 'singing/song'),
        'noun_person': ('cantante', 'singer'),
        'adjective': ('cantarín', 'fond of singing'),
    },
    'bail': {
        'verb_infinitive': ('bailar', 'to dance'),
        'noun_action': ('baile', 'dance'),
        'noun_person': ('bailarín', 'dancer'),
        'adjective': ('bailable', 'danceable'),
    },
    
    # -er/-ir verb families
    'com': {
        'verb_infinitive': ('comer', 'to eat'),
        'noun_action': ('comida', 'food/meal'),
        'noun_person': ('comensal', 'diner'),
        'adjective': ('comestible', 'edible'),
    },
    'beb': {
        'verb_infinitive': ('beber', 'to drink'),
        'noun_action': ('bebida', 'drink'),
        'noun_person': ('bebedor', 'drinker'),
        'adjective': ('bebible', 'drinkable'),
    },
    'viv': {
        'verb_infinitive': ('vivir', 'to live'),
        'noun_action': ('vida', 'life'),
        'noun_concept': ('vivencia', 'experience'),
        'adjective': ('vivo', 'alive/lively'),
        'adverb': ('vívidamente', 'vividly'),
    },
    'escrib': {
        'verb_infinitive': ('escribir', 'to write'),
        'noun_action': ('escritura', 'writing'),
        'noun_person': ('escritor', 'writer'),
        'noun_object': ('escrito', 'written text'),
        'adjective': ('escrito', 'written'),
    },
    
    # Adjective-based families
    'feliz': {
        'adjective': ('feliz', 'happy'),
        'noun_abstract': ('felicidad', 'happiness'),
        'adverb': ('felizmente', 'happily'),
        'verb': ('felicitar', 'to congratulate'),
    },
    'trist': {
        'adjective': ('triste', 'sad'),
        'noun_abstract': ('tristeza', 'sadness'),
        'adverb': ('tristemente', 'sadly'),
        'verb': ('entristecer', 'to sadden'),
    },
    'buen': {
        'adjective': ('bueno', 'good'),
        'noun_abstract': ('bondad', 'goodness'),
        'adverb': ('bien', 'well'),
    },
    'mal': {
        'adjective': ('malo', 'bad'),
        'noun_abstract': ('maldad', 'evil/badness'),
        'adverb': ('mal', 'badly'),
        'noun_person': ('malvado', 'villain'),
    },
    'bell': {
        'adjective': ('bello', 'beautiful'),
        'noun_abstract': ('belleza', 'beauty'),
        'adverb': ('bellamente', 'beautifully'),
    },
    
    # Noun-based families
    'amor': {
        'noun': ('amor', 'love'),
        'adjective': ('amoroso', 'loving'),
        'verb': ('amar', 'to love'),
        'adverb': ('amorosamente', 'lovingly'),
    },
    'libr': {
        'noun': ('libro', 'book'),
        'noun_place': ('librería', 'bookstore'),
        'noun_person': ('librero', 'bookseller'),
        'adjective': ('libresco', 'bookish'),
    },
    'casa': {
        'noun': ('casa', 'house'),
        'verb': ('casar', 'to marry'),
        'noun_related': ('casamiento', 'marriage'),
        'adjective': ('casero', 'homemade'),
    },
}


# Derivation patterns for generating word families
DERIVATION_PATTERNS = {
    # Noun to adjective
    '-oso': {'from': 'noun', 'to': 'adjective', 'meaning': 'full of', 
             'examples': [('fama', 'famoso'), ('poder', 'poderoso'), ('calor', 'caluroso')]},
    '-al': {'from': 'noun', 'to': 'adjective', 'meaning': 'related to',
            'examples': [('nación', 'nacional'), ('persona', 'personal'), ('centro', 'central')]},
    '-ivo': {'from': 'verb', 'to': 'adjective', 'meaning': 'having quality of',
             'examples': [('actuar', 'activo'), ('producir', 'productivo')]},
    
    # Verb to noun (action)
    '-ción': {'from': 'verb', 'to': 'noun', 'meaning': 'action/result',
              'examples': [('informar', 'información'), ('comunicar', 'comunicación')]},
    '-miento': {'from': 'verb', 'to': 'noun', 'meaning': 'action/process',
                'examples': [('sentir', 'sentimiento'), ('mover', 'movimiento')]},
    
    # Verb to noun (person)
    '-dor': {'from': 'verb', 'to': 'noun', 'meaning': 'one who does',
             'examples': [('trabajar', 'trabajador'), ('vender', 'vendedor')]},
    '-ante/-ente': {'from': 'verb', 'to': 'noun', 'meaning': 'one who does',
                    'examples': [('estudiar', 'estudiante'), ('servir', 'sirviente')]},
    
    # Adjective to noun (abstract)
    '-dad/-idad': {'from': 'adjective', 'to': 'noun', 'meaning': 'quality of',
                   'examples': [('feliz', 'felicidad'), ('real', 'realidad')]},
    '-eza': {'from': 'adjective', 'to': 'noun', 'meaning': 'quality of',
             'examples': [('triste', 'tristeza'), ('bello', 'belleza')]},
    
    # Adjective to adverb
    '-mente': {'from': 'adjective', 'to': 'adverb', 'meaning': 'in a manner',
               'examples': [('rápido', 'rápidamente'), ('fácil', 'fácilmente')]},
}


class WordFamilyExpander:
    """
    Expands vocabulary by finding related word forms.
    """
    
    def __init__(self):
        self.word_families = WORD_FAMILIES
        self.derivation_patterns = DERIVATION_PATTERNS
    
    def get_word_family(self, word: str) -> Optional[Dict]:
        """
        Get the complete word family for a word.
        
        Returns:
            dict with word forms and their translations
        """
        word_lower = word.lower().strip()
        
        # Check direct match in known families
        for root, family in self.word_families.items():
            for pos, (form, meaning) in family.items():
                if form == word_lower:
                    return {
                        'root': root,
                        'input_word': word,
                        'family': family,
                        'count': len(family),
                    }
        
        # Try to find by root extraction
        family = self._find_by_root(word_lower)
        if family:
            return family
        
        # Generate probable word forms using patterns
        generated = self._generate_word_forms(word_lower)
        if generated:
            return {
                'root': self._extract_probable_root(word_lower),
                'input_word': word,
                'family': generated,
                'count': len(generated),
                'generated': True,  # Flag that these are predictions
            }
        
        return None
    
    def _find_by_root(self, word: str) -> Optional[Dict]:
        """Try to find a word family by extracting the root."""
        # Check if word starts with any known root
        for root, family in self.word_families.items():
            if word.startswith(root):
                return {
                    'root': root,
                    'input_word': word,
                    'family': family,
                    'count': len(family),
                }
        return None
    
    def _extract_probable_root(self, word: str) -> str:
        """Extract a probable root from a word."""
        # Remove common endings
        endings = ['ar', 'er', 'ir', 'ción', 'sión', 'dad', 'idad', 
                   'mente', 'oso', 'osa', 'ivo', 'iva', 'dor', 'dora',
                   'ante', 'ente', 'eza']
        
        for ending in sorted(endings, key=len, reverse=True):
            if word.endswith(ending) and len(word) > len(ending) + 2:
                return word[:-len(ending)]
        
        # Return first portion as root
        return word[:max(3, len(word) - 2)]
    
    def _generate_word_forms(self, word: str) -> Dict:
        """Generate probable word forms using derivation patterns."""
        forms = {}
        root = self._extract_probable_root(word)
        
        # Determine if likely verb, noun, or adjective
        if word.endswith(('ar', 'er', 'ir')):
            # It's a verb, generate noun and adjective forms
            forms['verb_infinitive'] = (word, 'verb form')
            forms['noun_action'] = (root + 'ción', 'possible noun form')
            forms['noun_person'] = (root + 'dor', 'possible person form')
            forms['adjective'] = (root + 'do', 'possible adjective form')
            
        elif word.endswith(('o', 'a')):
            # Might be noun or adjective
            if word.endswith('o'):
                forms['adjective_masc'] = (word, 'masculine form')
                forms['adjective_fem'] = (word[:-1] + 'a', 'feminine form')
                forms['adverb'] = (word[:-1] + 'amente', 'adverb form')
            forms['noun'] = (word, 'noun form')
            
        elif word.endswith(('dad', 'idad')):
            # Abstract noun, derive adjective
            forms['noun_abstract'] = (word, 'abstract noun')
            adj_root = word.replace('idad', '').replace('dad', '')
            forms['adjective'] = (adj_root, 'possible adjective')
        
        return forms if forms else None
    
    def get_related_words(self, word: str, limit: int = 5) -> List[Dict]:
        """
        Get a list of related words with their translations.
        
        Returns:
            List of dicts with spanish, english, part_of_speech
        """
        family = self.get_word_family(word)
        if not family:
            return []
        
        related = []
        for pos, (spanish, english) in family.get('family', {}).items():
            related.append({
                'spanish': spanish,
                'english': english,
                'part_of_speech': pos.replace('_', ' '),
            })
        
        return related[:limit]
    
    def get_derivation_pattern(self, word: str) -> Optional[Dict]:
        """
        Identify the derivation pattern used in a word.
        Helps learners understand how words are formed.
        """
        word_lower = word.lower()
        
        for pattern, info in self.derivation_patterns.items():
            endings = pattern.strip('-').split('/')
            for ending in endings:
                if word_lower.endswith(ending):
                    return {
                        'pattern': pattern,
                        'from': info['from'],
                        'to': info['to'],
                        'meaning': info['meaning'],
                        'examples': info['examples'],
                    }
        return None
    
    def learn_pattern_explanation(self, pattern: str) -> str:
        """
        Get an explanation of a derivation pattern for learning.
        """
        explanations = {
            '-oso': "Adding -oso to a noun creates an adjective meaning 'full of that quality'. "
                   "Example: fama (fame) → famoso (famous, literally 'full of fame')",
            '-ción': "Adding -ción to a verb creates a noun for the action or result. "
                    "Example: informar (to inform) → información (information)",
            '-dor': "Adding -dor to a verb creates a noun meaning 'one who does the action'. "
                   "Example: trabajar (to work) → trabajador (worker)",
            '-mente': "Adding -mente to a feminine adjective creates an adverb. "
                     "Example: rápida (quick-fem) → rápidamente (quickly)",
            '-dad': "Adding -dad to an adjective creates an abstract noun for the quality. "
                   "Example: real (real) → realidad (reality)",
        }
        
        return explanations.get(pattern, f"The pattern {pattern} is used to derive new words.")


# Singleton instance
word_family_expander = WordFamilyExpander()
