"""
Z32 Nexus - Vocabulary Processor
Translation engine with caching, rate limiting, and CSV export
"""

import logging
import time
import re
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Optional, Set
from collections import OrderedDict

from deep_translator import GoogleTranslator

from database import db, Vocabulary, TranslationCache

logger = logging.getLogger(__name__)


# Common English stop words to filter out
STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
    'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those',
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us',
    'them', 'my', 'your', 'his', 'its', 'our', 'their', 'what', 'which',
    'who', 'whom', 'when', 'where', 'why', 'how', 'all', 'each', 'every',
    'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
    'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just',
    'also', 'now', 'here', 'there', 'then', 'once', 'if', 'else', 'because',
    'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below',
    'between', 'under', 'again', 'further', 'any', 'up', 'down', 'out', 'off',
    'over', 'am', 'being', 'having', 'doing', 'while', 'until', 'against',
    'yet', 'however', 'although', 'though', 'even', 'still', 'already',
    'always', 'never', 'sometimes', 'often', 'usually', 'perhaps', 'maybe'
}


class VocabProcessor:
    """
    Processes text to extract vocabulary and translate to Spanish.
    Features:
    - Word extraction and filtering
    - Rate-limited translation with caching
    - CSV export in Anki format
    """
    
    def __init__(self):
        self.translator = GoogleTranslator(source='en', target='es')
        self._translation_cache = {}
        self._last_request_time = 0
        self._min_request_interval = 0.2  # 200ms = 5 requests per second
    
    def extract_words(self, text: str, 
                     min_length: int = 3,
                     remove_stop_words: bool = True) -> List[str]:
        """
        Extract unique words from text.
        
        Args:
            text: Input text to process
            min_length: Minimum word length (default: 3)
            remove_stop_words: Whether to filter stop words
            
        Returns:
            List of unique words
        """
        # Normalize text
        text = text.lower()
        
        # Extract words (only letters)
        words = re.findall(r'\b[a-z]+\b', text)
        
        # Filter by length
        words = [w for w in words if len(w) >= min_length]
        
        # Remove stop words
        if remove_stop_words:
            words = [w for w in words if w not in STOP_WORDS]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_words = []
        for word in words:
            if word not in seen:
                seen.add(word)
                unique_words.append(word)
        
        return unique_words
    
    def _rate_limit(self):
        """Enforce rate limiting between API calls"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_request_interval:
            time.sleep(self._min_request_interval - elapsed)
        self._last_request_time = time.time()
    
    def _get_cached_translation(self, word: str) -> Optional[str]:
        """Check database cache for translation"""
        # Check memory cache first
        if word in self._translation_cache:
            return self._translation_cache[word]
        
        # Check database cache
        session = db.get_session()
        try:
            cached = session.query(TranslationCache).filter_by(
                source_text=word,
                source_lang='en',
                target_lang='es'
            ).first()
            
            if cached:
                self._translation_cache[word] = cached.translated_text
                return cached.translated_text
        finally:
            session.close()
        
        return None
    
    def _cache_translation(self, word: str, translation: str):
        """Cache translation in database and memory"""
        self._translation_cache[word] = translation
        
        session = db.get_session()
        try:
            cached = TranslationCache(
                source_text=word,
                source_lang='en',
                target_lang='es',
                translated_text=translation
            )
            session.merge(cached)
            session.commit()
        except Exception as e:
            logger.error(f"Failed to cache translation: {e}")
            session.rollback()
        finally:
            session.close()
    
    def translate_word(self, word: str, retries: int = 3) -> Optional[str]:
        """
        Translate a single word from English to Spanish.
        Uses caching and rate limiting.
        """
        # Check cache first
        cached = self._get_cached_translation(word)
        if cached:
            return cached
        
        # Rate limit
        self._rate_limit()
        
        # Try translation with retries
        for attempt in range(retries):
            try:
                translation = self.translator.translate(word)
                if translation:
                    self._cache_translation(word, translation)
                    return translation
            except Exception as e:
                logger.warning(f"Translation attempt {attempt + 1} failed for '{word}': {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        
        logger.error(f"Failed to translate '{word}' after {retries} attempts")
        return None
    
    def translate_batch(self, words: List[str], 
                       progress_callback=None) -> List[Tuple[str, str]]:
        """
        Translate a batch of words.
        
        Args:
            words: List of English words
            progress_callback: Optional callback(current, total)
            
        Returns:
            List of (english, spanish) tuples
        """
        results = []
        total = len(words)
        
        for i, word in enumerate(words):
            translation = self.translate_word(word)
            if translation:
                results.append((word, translation))
            
            if progress_callback:
                progress_callback(i + 1, total)
        
        return results
    
    def add_to_vocabulary(self, english: str, spanish: str, 
                         context: str = '', category: str = 'general') -> bool:
        """Add a word to the vocabulary database"""
        session = db.get_session()
        try:
            # Check if word already exists
            existing = session.query(Vocabulary).filter_by(english=english.lower()).first()
            if existing:
                logger.info(f"Word '{english}' already exists in vocabulary")
                return False
            
            vocab = Vocabulary(
                english=english.lower(),
                spanish=spanish.lower(),
                context=context,
                category=category
            )
            session.add(vocab)
            session.commit()
            
            # Update today's progress
            from database import UserProgress
            from datetime import date
            
            today = date.today()
            progress = session.query(UserProgress).filter_by(date=today).first()
            if progress:
                progress.words_learned = (progress.words_learned or 0) + 1
                session.commit()
            
            logger.info(f"Added word to vocabulary: {english} -> {spanish}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add word to vocabulary: {e}")
            session.rollback()
            return False
        finally:
            session.close()
    
    def export_to_csv(self, output_path: str = None, 
                     words: List[Tuple[str, str]] = None) -> str:
        """
        Export vocabulary to CSV file in Anki format.
        
        Args:
            output_path: Optional output path (default: my_anki_deck.csv)
            words: Optional list of (english, spanish) tuples.
                   If None, exports all vocabulary from database.
        
        Returns:
            Path to the created CSV file
        """
        if output_path is None:
            output_path = Path(__file__).parent.parent / 'data' / 'my_anki_deck.csv'
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Get words from database if not provided
        if words is None:
            session = db.get_session()
            try:
                vocab_items = session.query(Vocabulary).all()
                words = [(v.english, v.spanish) for v in vocab_items]
            finally:
                session.close()
        
        # Append to CSV (Anki format: front;back)
        file_exists = output_path.exists()
        
        with open(output_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            
            for english, spanish in words:
                writer.writerow([english, spanish])
        
        logger.info(f"Exported {len(words)} words to {output_path}")
        return str(output_path)
    
    def process_text(self, text: str, 
                    progress_callback=None) -> Tuple[List[Tuple[str, str]], int]:
        """
        Full pipeline: extract words, translate, and add to vocabulary.
        
        Args:
            text: Input text to process
            progress_callback: Optional callback(current, total)
            
        Returns:
            (list of (english, spanish) tuples, number of new words added)
        """
        # Extract words
        words = self.extract_words(text)
        logger.info(f"Extracted {len(words)} unique words")
        
        if not words:
            return [], 0
        
        # Translate
        translations = self.translate_batch(words, progress_callback)
        logger.info(f"Translated {len(translations)} words")
        
        # Add to vocabulary
        added_count = 0
        for english, spanish in translations:
            if self.add_to_vocabulary(english, spanish):
                added_count += 1
        
        logger.info(f"Added {added_count} new words to vocabulary")
        return translations, added_count


# Singleton processor instance
vocab_processor = VocabProcessor()
