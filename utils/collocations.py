"""
Z32 Nexus - Collocations Database
Feature 11: Collocations Database

Provides common word pairings and their Spanish equivalents.
Helps learners avoid literal translations and speak more naturally.

Example: English "make a decision" → Spanish "tomar una decisión" (NOT "hacer una decisión")
"""

import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# Common English-Spanish collocations
# Format: english_collocation -> (spanish_equivalent, literal_wrong_translation, notes)
COLLOCATIONS = {
    # "Make" collocations
    'make a decision': ('tomar una decisión', 'hacer una decisión', 
                        'In Spanish, you "take" a decision, not "make" it'),
    'make a mistake': ('cometer un error', 'hacer un error',
                       'In Spanish, you "commit" a mistake'),
    'make money': ('ganar dinero', 'hacer dinero',
                   'In Spanish, you "earn/win" money'),
    'make friends': ('hacer amigos', None, 
                     'This one actually uses "hacer"!'),
    'make an effort': ('hacer un esfuerzo', None,
                       'This one uses "hacer" too'),
    'make progress': ('hacer progresos', None,
                       'Uses "hacer" - progress is made'),
    'make the bed': ('hacer la cama', None,
                     'Uses "hacer" - literally make the bed'),
    'make a phone call': ('hacer una llamada', None,
                           'Uses "hacer" for phone calls'),
    
    # "Take" collocations
    'take a shower': ('ducharse / tomar una ducha', 'tomar una lluvia',
                      'Usually reflexive "ducharse" or "tomar una ducha"'),
    'take a walk': ('dar un paseo', 'tomar un paseo',
                    'In Spanish, you "give" a walk'),
    'take a photo': ('sacar una foto', 'tomar una foto',
                     'More common to "sacar" (take out) a photo'),
    'take a break': ('tomar un descanso / descansar', None,
                     '"Tomar" works or just use verb "descansar"'),
    'take notes': ('tomar apuntes', None,
                   '"Tomar" works here'),
    'take medicine': ('tomar medicinas', None,
                      '"Tomar" is correct for medicine'),
    'take time': ('llevar tiempo', 'tomar tiempo',
                  'In Spanish, time "carries" (lleva)'),
    
    # "Have" collocations
    'have breakfast': ('desayunar', 'tener desayuno',
                       'Spanish uses specific verb "desayunar"'),
    'have lunch': ('almorzar', 'tener almuerzo',
                   'Spanish uses specific verb "almorzar"'),
    'have dinner': ('cenar', 'tener cena',
                    'Spanish uses specific verb "cenar"'),
    'have a good time': ('pasarlo bien', 'tener un buen tiempo',
                         'In Spanish, you "pass it well"'),
    'have fun': ('divertirse', 'tener diversión',
                 'Reflexive verb "to amuse oneself"'),
    'have a dream': ('tener un sueño / soñar', None,
                     '"Tener" works, or use verb "soñar"'),
    
    # "Do" collocations
    'do homework': ('hacer la tarea / los deberes', None,
                    'Uses "hacer" - tarea in Latin America, deberes in Spain'),
    'do exercise': ('hacer ejercicio', None,
                    'Uses "hacer" for exercise'),
    'do the dishes': ('lavar los platos / fregar los platos', 'hacer los platos',
                      'You "wash" the dishes in Spanish'),
    'do business': ('hacer negocios', None,
                    'Uses "hacer" for business'),
    'do laundry': ('lavar la ropa', 'hacer la lavandería',
                   'You "wash" the clothes'),
    
    # "Get" collocations (tricky - many translations)
    'get angry': ('enfadarse / enojarse', 'conseguir enojado',
                  'Reflexive verb - "to anger oneself"'),
    'get married': ('casarse', 'conseguir casado',
                    'Reflexive verb - "to marry oneself"'),
    'get ready': ('prepararse', 'conseguir listo',
                  'Reflexive - "to prepare oneself"'),
    'get lost': ('perderse', 'conseguir perdido',
                 'Reflexive - "to lose oneself"'),
    'get better': ('mejorar(se)', 'conseguir mejor',
                   'Verb "mejorar" = to improve'),
    'get tired': ('cansarse', 'conseguir cansado',
                  'Reflexive verb'),
    
    # "Give" collocations
    'give a hand': ('echar una mano', 'dar una mano',
                    'You "throw" a hand in Spanish'),
    'give a hug': ('dar un abrazo', None,
                   '"Dar" works here'),
    'give a kiss': ('dar un beso', None,
                    '"Dar" works for kisses'),
    'give up': ('rendirse / darse por vencido', 'dar arriba',
                'Reflexive "to surrender" or "give oneself for defeated"'),
    
    # Weather expressions
    'it is hot': ('hace calor', 'es caliente / está caliente',
                  'Weather uses "hacer" - it "makes" heat'),
    'it is cold': ('hace frío', 'es frío',
                   'Weather uses "hacer" - it "makes" cold'),
    'it is windy': ('hace viento', None,
                    'Weather uses "hacer"'),
    'it is sunny': ('hace sol', None,
                    'The sun "makes" - hace sol'),
    'it is raining': ('está lloviendo / llueve', 'es lloviendo',
                      'Use estar for continuous or simple verb'),
    
    # Age expressions
    'to be X years old': ('tener X años', 'ser X años viejo',
                          'Spanish uses "tener" (to have) for age'),
    'how old are you': ('cuántos años tienes', 'qué tan viejo eres',
                        'How many years do you have?'),
    
    # Other common ones
    'pay attention': ('prestar atención', 'pagar atención',
                      'You "lend" attention in Spanish'),
    'catch a cold': ('resfriarse / coger un resfriado', 'atrapar un frío',
                     'Reflexive verb "to cold oneself" or "catch a cold"'),
    'fall asleep': ('quedarse dormido / dormirse', 'caer dormido',
                    'Reflexive "to stay asleep" or "to sleep oneself"'),
    'be in a hurry': ('tener prisa', 'estar en prisa',
                      'You "have" hurry in Spanish'),
    'be hungry': ('tener hambre', 'ser hambriento',
                  'You "have" hunger in Spanish'),
    'be thirsty': ('tener sed', 'ser sediento',
                   'You "have" thirst in Spanish'),
    'be afraid': ('tener miedo', 'ser asustado',
                  'You "have" fear in Spanish'),
    'be right': ('tener razón', 'ser correcto',
                 'You "have" reason in Spanish'),
    'be wrong': ('estar equivocado / no tener razón', 'ser equivocado',
                 'Use "estar" or "not have reason"'),
    'be lucky': ('tener suerte', 'ser afortunado',
                 'You "have" luck in Spanish'),
}


# False friends - words that look similar but mean different things
FALSE_FRIENDS = {
    'actual': {
        'spanish_lookalike': 'actual',
        'lookalike_meaning': 'current, present',
        'correct_translation': 'real, verdadero',
        'example_error': '"actual" means current, not real!',
    },
    'embarrassed': {
        'spanish_lookalike': 'embarazada',
        'lookalike_meaning': 'pregnant',
        'correct_translation': 'avergonzado/a',
        'example_error': '"embarazada" means pregnant, not embarrassed!',
    },
    'library': {
        'spanish_lookalike': 'librería',
        'lookalike_meaning': 'bookstore',
        'correct_translation': 'biblioteca',
        'example_error': '"librería" is a bookstore, "biblioteca" is a library',
    },
    'sensible': {
        'spanish_lookalike': 'sensible',
        'lookalike_meaning': 'sensitive',
        'correct_translation': 'sensato/a',
        'example_error': '"sensible" in Spanish means sensitive',
    },
    'exit': {
        'spanish_lookalike': 'éxito',
        'lookalike_meaning': 'success',
        'correct_translation': 'salida',
        'example_error': '"éxito" means success, "salida" is an exit',
    },
    'carpet': {
        'spanish_lookalike': 'carpeta',
        'lookalike_meaning': 'folder/binder',
        'correct_translation': 'alfombra',
        'example_error': '"carpeta" is a folder, "alfombra" is a carpet',
    },
    'argument': {
        'spanish_lookalike': 'argumento',
        'lookalike_meaning': 'plot (of a story)',
        'correct_translation': 'discusión/pelea',
        'example_error': '"argumento" often means plot, not a fight',
    },
    'assist': {
        'spanish_lookalike': 'asistir',
        'lookalike_meaning': 'to attend',
        'correct_translation': 'ayudar',
        'example_error': '"asistir" means to attend, "ayudar" means to help',
    },
    'realize': {
        'spanish_lookalike': 'realizar',
        'lookalike_meaning': 'to carry out/accomplish',
        'correct_translation': 'darse cuenta',
        'example_error': '"realizar" means to accomplish, use "darse cuenta" for realize',
    },
    'support': {
        'spanish_lookalike': 'soportar',
        'lookalike_meaning': 'to tolerate/bear',
        'correct_translation': 'apoyar',
        'example_error': '"soportar" means to tolerate, "apoyar" means to support',
    },
}


class CollocationsDatabase:
    """
    Manages collocation lookups and false friend detection.
    """
    
    def __init__(self):
        self.collocations = COLLOCATIONS
        self.false_friends = FALSE_FRIENDS
    
    def lookup_collocation(self, english_phrase: str) -> Optional[Dict]:
        """
        Look up the Spanish equivalent of an English collocation.
        
        Returns:
            dict with spanish, wrong_translation (if applicable), notes
        """
        english_lower = english_phrase.lower().strip()
        
        # Direct lookup
        if english_lower in self.collocations:
            spanish, wrong, notes = self.collocations[english_lower]
            return {
                'english': english_phrase,
                'spanish': spanish,
                'wrong_translation': wrong,
                'notes': notes,
                'is_common_error': wrong is not None,
            }
        
        # Partial match - find collocations containing key words
        matches = []
        words = english_lower.split()
        for coll, data in self.collocations.items():
            for word in words:
                if len(word) > 3 and word in coll:
                    matches.append({
                        'english': coll,
                        'spanish': data[0],
                        'notes': data[2],
                    })
                    break
        
        if matches:
            return {
                'english': english_phrase,
                'direct_match': False,
                'similar_collocations': matches[:5],
            }
        
        return None
    
    def check_false_friend(self, word: str) -> Optional[Dict]:
        """
        Check if a word might be confused with a false friend.
        
        Returns:
            dict with warning information if it's a false friend
        """
        word_lower = word.lower().strip()
        
        if word_lower in self.false_friends:
            ff = self.false_friends[word_lower]
            return {
                'english_word': word,
                'spanish_lookalike': ff['spanish_lookalike'],
                'lookalike_meaning': ff['lookalike_meaning'],
                'correct_translation': ff['correct_translation'],
                'warning': ff['example_error'],
            }
        
        return None
    
    def get_collocations_for_verb(self, verb: str) -> List[Dict]:
        """
        Get all collocations that use a specific verb.
        
        Args:
            verb: English verb like 'make', 'take', 'have', etc.
        
        Returns:
            List of collocation entries
        """
        results = []
        verb_lower = verb.lower()
        
        for english, (spanish, wrong, notes) in self.collocations.items():
            if english.startswith(verb_lower + ' '):
                results.append({
                    'english': english,
                    'spanish': spanish,
                    'wrong_translation': wrong,
                    'notes': notes,
                })
        
        return results
    
    def get_random_collocation(self, category: str = None) -> Dict:
        """
        Get a random collocation for learning/quizzing.
        
        Args:
            category: Optional category like 'weather', 'food', etc.
        """
        import random
        
        items = list(self.collocations.items())
        english, (spanish, wrong, notes) = random.choice(items)
        
        return {
            'english': english,
            'spanish': spanish,
            'wrong_translation': wrong,
            'notes': notes,
            'is_common_error': wrong is not None,
        }
    
    def get_all_false_friends(self) -> List[Dict]:
        """Get all false friends for study."""
        return [
            {
                'english': word,
                **data
            }
            for word, data in self.false_friends.items()
        ]
    
    def quiz_collocation(self, english: str, user_answer: str) -> Dict:
        """
        Check if a user's translation of a collocation is correct.
        
        Returns:
            dict with is_correct, correct_answer, feedback
        """
        lookup = self.lookup_collocation(english)
        if not lookup:
            return {'error': 'Collocation not found in database'}
        
        user_lower = user_answer.lower().strip()
        correct_options = lookup['spanish'].lower().split(' / ')
        
        is_correct = any(user_lower in opt or opt in user_lower 
                         for opt in correct_options)
        
        # Check if they gave the common wrong answer
        gave_wrong = False
        if lookup.get('wrong_translation'):
            wrong_lower = lookup['wrong_translation'].lower()
            if wrong_lower in user_lower:
                gave_wrong = True
        
        return {
            'is_correct': is_correct,
            'correct_answer': lookup['spanish'],
            'gave_common_mistake': gave_wrong,
            'notes': lookup.get('notes', ''),
            'feedback': self._generate_feedback(is_correct, gave_wrong, lookup),
        }
    
    def _generate_feedback(self, is_correct: bool, gave_wrong: bool, 
                            lookup: Dict) -> str:
        """Generate helpful feedback for the user."""
        if is_correct:
            return "¡Perfecto! Great job with this collocation!"
        elif gave_wrong:
            return (f"Close, but that's a common mistake! {lookup.get('notes', '')} "
                   f"The correct answer is: {lookup['spanish']}")
        else:
            return f"Not quite. The correct answer is: {lookup['spanish']}"


# Singleton instance
collocations_db = CollocationsDatabase()
