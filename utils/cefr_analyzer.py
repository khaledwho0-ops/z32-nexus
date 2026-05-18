"""
Z32 Nexus - CEFR Analyzer
Feature 16: Reading Level Analyzer
Feature 27: CEFR Level Estimation

Analyzes text difficulty and estimates user's CEFR level based on vocabulary.
CEFR Levels: A1, A2, B1, B2, C1, C2
"""

import logging
import re
from typing import Dict, List, Tuple, Optional
from collections import Counter

logger = logging.getLogger(__name__)


# Vocabulary size estimates by CEFR level
CEFR_VOCAB_SIZES = {
    'A1': (0, 500),      # Beginner
    'A2': (501, 1000),   # Elementary  
    'B1': (1001, 2500),  # Intermediate
    'B2': (2501, 5000),  # Upper Intermediate
    'C1': (5001, 10000), # Advanced
    'C2': (10001, 25000) # Proficiency
}


# Common words by CEFR level (core vocabulary)
# These are the most frequent Spanish words at each level
A1_WORDS = {
    'hola', 'adiós', 'sí', 'no', 'gracias', 'por favor', 'buenos días',
    'yo', 'tú', 'él', 'ella', 'nosotros', 'ellos', 'ser', 'estar', 'tener',
    'casa', 'familia', 'agua', 'comida', 'comer', 'beber', 'dormir',
    'uno', 'dos', 'tres', 'cuatro', 'cinco', 'grande', 'pequeño',
    'bueno', 'malo', 'blanco', 'negro', 'rojo', 'azul', 'verde',
    'hoy', 'mañana', 'ayer', 'ahora', 'después', 'antes', 'siempre',
    'madre', 'padre', 'hermano', 'hermana', 'hijo', 'hija', 'amigo',
    'qué', 'quién', 'dónde', 'cuándo', 'por qué', 'cómo', 'cuánto',
    'ir', 'venir', 'hacer', 'decir', 'ver', 'saber', 'poder', 'querer',
}

A2_WORDS = {
    'trabajar', 'estudiar', 'vivir', 'ciudad', 'país', 'tiempo', 'año',
    'mes', 'semana', 'día', 'hora', 'minuto', 'dinero', 'tienda', 'comprar',
    'vender', 'calle', 'coche', 'tren', 'avión', 'hotel', 'restaurante',
    'desayuno', 'almuerzo', 'cena', 'café', 'leche', 'pan', 'carne',
    'pescado', 'fruta', 'verdura', 'sol', 'lluvia', 'calor', 'frío',
    'feliz', 'triste', 'cansado', 'enfermo', 'joven', 'viejo', 'nuevo',
    'cerca', 'lejos', 'izquierda', 'derecha', 'arriba', 'abajo', 'dentro',
    'fuera', 'entre', 'sobre', 'bajo', 'desde', 'hasta', 'hacia', 'contra',
    'pensar', 'creer', 'sentir', 'esperar', 'necesitar', 'gustar', 'parecer',
}

B1_WORDS = {
    'ambiente', 'aspecto', 'asunto', 'cantidad', 'capacidad', 'carácter',
    'condición', 'conocimiento', 'consecuencia', 'desarrollo', 'diferencia',
    'efecto', 'esfuerzo', 'espacio', 'experiencia', 'función', 'gobierno',
    'historia', 'imagen', 'información', 'interés', 'manera', 'medida',
    'momento', 'movimiento', 'nivel', 'objeto', 'opinión', 'orden',
    'organización', 'papel', 'parte', 'período', 'población', 'posibilidad',
    'presencia', 'proceso', 'producción', 'programa', 'proyecto', 'razón',
    'realidad', 'resultado', 'sentido', 'servicio', 'sistema', 'situación',
    'sociedad', 'tipo', 'valor', 'verdad', 'conseguir', 'convertir',
    'cumplir', 'establecer', 'existir', 'formar', 'mantener', 'ofrecer',
}

B2_WORDS = {
    'abstracto', 'abundante', 'acceso', 'adecuado', 'administración',
    'advertir', 'afirmar', 'alcanzar', 'alternativa', 'análisis', 'ámbito',
    'aplicar', 'apoyar', 'aproximadamente', 'asumir', 'beneficio', 'breve',
    'característico', 'categoría', 'científico', 'circunstancia', 'clave',
    'coherente', 'competencia', 'complejo', 'componente', 'comportamiento',
    'concepto', 'conciencia', 'conclusión', 'concreto', 'conflicto',
    'considerar', 'constituir', 'contexto', 'contribuir', 'criterio',
    'debate', 'definir', 'demostrar', 'destacar', 'determinar', 'discurso',
    'disponer', 'distribución', 'diverso', 'dominio', 'económico', 'elaborar',
}

C1_WORDS = {
    'abordar', 'acercar', 'acoger', 'acontecimiento', 'acudir', 'adquirir',
    'afectar', 'agudo', 'ajeno', 'allegado', 'amenaza', 'ampliar', 'ánimo',
    'anular', 'apreciar', 'arrojar', 'articular', 'atribuir', 'auge',
    'autonomía', 'ceder', 'cifra', 'concebir', 'configurar', 'conjugar',
    'contradicción', 'dar cuenta', 'decadencia', 'deficiencia', 'desafío',
    'desempeñar', 'desprender', 'deterioro', 'dilema', 'discrepancia',
    'disminuir', 'disputa', 'distorsión', 'eficacia', 'eludir', 'emergente',
    'emprender', 'encauzar', 'enfoque', 'entorno', 'escasez', 'esclarecer',
}

C2_WORDS = {
    'abolir', 'abstenerse', 'acaparar', 'acechar', 'acometer', 'acotar',
    'acrecentar', 'adolecer', 'aducir', 'afianzar', 'aflorar', 'agudizar',
    'ahondar', 'alentar', 'alegar', 'amalgamar', 'ameritar', 'amortiguar',
    'anquilosado', 'anteponer', 'apaciguar', 'aquilatar', 'arbitrar',
    'arremeter', 'arribar', 'ataviar', 'atenuar', 'atisbar', 'aunar',
    'azuzar', 'cavilar', 'cernirse', 'columbrar', 'compeler', 'concomitante',
    'confabular', 'conjeturar', 'consignar', 'contravenir', 'corroborar',
}


# Sentence complexity indicators
COMPLEX_STRUCTURES = {
    'B1': [' aunque ', ' porque ', ' cuando ', ' mientras ', ' si '],
    'B2': [' a pesar de ', ' sin embargo ', ' no obstante ', ' dado que ', ' puesto que '],
    'C1': [' en virtud de ', ' a raíz de ', ' en aras de ', ' habida cuenta ', ' a tenor de '],
    'C2': [' merced a ', ' so pretexto de ', ' a expensas de ', ' en detrimento de '],
}


class CEFRAnalyzer:
    """
    Analyzes text and vocabulary for CEFR level estimation.
    """
    
    def __init__(self):
        self.level_words = {
            'A1': A1_WORDS,
            'A2': A2_WORDS,
            'B1': B1_WORDS,
            'B2': B2_WORDS,
            'C1': C1_WORDS,
            'C2': C2_WORDS,
        }
        self.vocab_sizes = CEFR_VOCAB_SIZES
    
    def analyze_text(self, text: str) -> Dict:
        """
        Analyze a Spanish text and estimate its CEFR difficulty level.
        
        Returns:
            dict with level, confidence, word_stats, complexity_markers
        """
        # Normalize text
        text_lower = text.lower()
        
        # Extract words
        words = self._extract_words(text)
        unique_words = set(words)
        
        # Analyze word levels
        word_levels = self._categorize_words(unique_words)
        
        # Calculate average word length (indicator of complexity)
        avg_word_length = sum(len(w) for w in words) / max(len(words), 1)
        
        # Check for complex structures
        complexity_markers = self._find_complexity_markers(text_lower)
        
        # Estimate overall level
        level, confidence = self._estimate_level(word_levels, complexity_markers, avg_word_length)
        
        return {
            'estimated_level': level,
            'confidence': confidence,
            'total_words': len(words),
            'unique_words': len(unique_words),
            'average_word_length': round(avg_word_length, 1),
            'word_levels': word_levels,
            'complexity_markers': complexity_markers,
            'unknown_words': list(unique_words - self._get_all_known_words())[:20],
            'reading_tips': self._get_reading_tips(level),
        }
    
    def _extract_words(self, text: str) -> List[str]:
        """Extract words from text."""
        # Remove punctuation and split
        text = re.sub(r'[^\w\sáéíóúüñ]', ' ', text.lower())
        words = [w for w in text.split() if len(w) >= 2]
        return words
    
    def _categorize_words(self, words: set) -> Dict[str, List[str]]:
        """Categorize words by their CEFR level."""
        categorized = {level: [] for level in self.level_words}
        categorized['unknown'] = []
        
        for word in words:
            found = False
            for level, level_words in self.level_words.items():
                if word in level_words:
                    categorized[level].append(word)
                    found = True
                    break
            if not found:
                categorized['unknown'].append(word)
        
        return categorized
    
    def _find_complexity_markers(self, text: str) -> Dict[str, List[str]]:
        """Find grammatical structures that indicate complexity level."""
        found = {}
        
        for level, structures in COMPLEX_STRUCTURES.items():
            matches = [s.strip() for s in structures if s in text]
            if matches:
                found[level] = matches
        
        return found
    
    def _estimate_level(self, word_levels: Dict, complexity_markers: Dict,
                        avg_word_length: float) -> Tuple[str, float]:
        """Estimate overall CEFR level and confidence."""
        # Weight words by level
        level_weights = {'A1': 1, 'A2': 2, 'B1': 3, 'B2': 4, 'C1': 5, 'C2': 6, 'unknown': 4}
        
        total_weighted = 0
        total_count = 0
        
        for level, words in word_levels.items():
            count = len(words)
            total_weighted += level_weights.get(level, 3) * count
            total_count += count
        
        if total_count == 0:
            return 'A1', 0.0
        
        avg_level = total_weighted / total_count
        
        # Adjust for complexity markers
        if 'C2' in complexity_markers:
            avg_level += 0.5
        elif 'C1' in complexity_markers:
            avg_level += 0.3
        elif 'B2' in complexity_markers:
            avg_level += 0.2
        
        # Adjust for word length
        if avg_word_length > 8:
            avg_level += 0.3
        elif avg_word_length > 6:
            avg_level += 0.1
        
        # Convert to CEFR level
        levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
        level_index = min(int(avg_level) - 1, 5)
        level_index = max(level_index, 0)
        
        # Calculate confidence based on known words ratio
        known_count = sum(len(words) for level, words in word_levels.items() if level != 'unknown')
        confidence = known_count / max(total_count, 1)
        
        return levels[level_index], round(confidence, 2)
    
    def _get_all_known_words(self) -> set:
        """Get all known vocabulary words."""
        all_words = set()
        for words in self.level_words.values():
            all_words.update(words)
        return all_words
    
    def _get_reading_tips(self, level: str) -> List[str]:
        """Get reading tips based on level."""
        tips = {
            'A1': [
                "Focus on understanding the main topic",
                "Look for cognates (similar words in English)",
                "Don't worry about every word - get the gist first",
            ],
            'A2': [
                "Try to understand complete sentences",
                "Pay attention to common verb forms",
                "Build vocabulary from context clues",
            ],
            'B1': [
                "Notice connecting words and text structure",
                "Start identifying the author's opinion",
                "Practice summarizing paragraphs",
            ],
            'B2': [
                "Analyze the author's style and tone",
                "Notice idioms and figurative language",
                "Read without translating in your head",
            ],
            'C1': [
                "Focus on nuance and subtle meanings",
                "Identify cultural references",
                "Practice speed reading techniques",
            ],
            'C2': [
                "Appreciate stylistic choices",
                "Read specialized or academic content",
                "Analyze rhetorical devices",
            ],
        }
        return tips.get(level, tips['A1'])
    
    def estimate_user_level(self, known_vocab_count: int, 
                            accuracy_rate: float,
                            grammar_score: int = 50) -> Dict:
        """
        Estimate user's overall CEFR level based on their vocabulary size
        and performance metrics.
        
        Args:
            known_vocab_count: Number of words the user has mastered
            accuracy_rate: Flashcard accuracy (0-100)
            grammar_score: Grammar drill score (0-100)
        
        Returns:
            dict with estimated level, confidence, and recommendations
        """
        # Determine level from vocabulary size
        vocab_level = 'A1'
        for level, (min_size, max_size) in self.vocab_sizes.items():
            if min_size <= known_vocab_count <= max_size:
                vocab_level = level
                break
            elif known_vocab_count > max_size:
                vocab_level = level
        
        # Adjust for accuracy (high accuracy = might be ready for next level)
        levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
        current_index = levels.index(vocab_level)
        
        readiness_score = (accuracy_rate + grammar_score) / 2
        
        if readiness_score >= 85 and current_index < 5:
            ready_for_next = True
            next_level = levels[current_index + 1]
        else:
            ready_for_next = False
            next_level = vocab_level
        
        # Calculate words needed for next level
        if current_index < 5:
            next_level_min = self.vocab_sizes[levels[current_index + 1]][0]
            words_to_next = max(0, next_level_min - known_vocab_count)
        else:
            words_to_next = 0
        
        return {
            'current_level': vocab_level,
            'vocabulary_count': known_vocab_count,
            'accuracy_rate': accuracy_rate,
            'ready_for_next_level': ready_for_next,
            'next_level': next_level if ready_for_next else None,
            'words_to_next_level': words_to_next,
            'recommendations': self._get_level_recommendations(vocab_level, readiness_score),
        }
    
    def _get_level_recommendations(self, level: str, readiness: float) -> List[str]:
        """Get personalized recommendations based on level and performance."""
        recs = []
        
        if readiness < 60:
            recs.append("Focus on reviewing current vocabulary before adding new words")
            recs.append("Practice with easier content to build confidence")
        elif readiness < 75:
            recs.append("Good progress! Mix new words with regular review")
            recs.append("Try listening exercises to reinforce learning")
        else:
            recs.append("Excellent! You're ready for more challenging content")
            recs.append("Start incorporating content at the next level")
        
        # Level-specific recommendations
        level_recs = {
            'A1': ["Master common greetings and essential verbs", "Focus on present tense"],
            'A2': ["Build vocabulary for daily life situations", "Learn past tense basics"],
            'B1': ["Start reading Spanish news articles", "Practice expressing opinions"],
            'B2': ["Watch Spanish TV series without subtitles", "Learn subjunctive mood"],
            'C1': ["Read Spanish literature", "Work on idiomatic expressions"],
            'C2': ["Explore regional dialects", "Study Spanish linguistics"],
        }
        
        recs.extend(level_recs.get(level, []))
        return recs[:5]  # Return top 5 recommendations


# Singleton instance
cefr_analyzer = CEFRAnalyzer()
