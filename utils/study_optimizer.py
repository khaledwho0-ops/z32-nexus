"""
Z32 Nexus - Study Optimizer
Feature 29: Optimal Study Time Detector
Feature 25: Weak Areas Identifier

Tracks performance patterns and detects optimal study times and weak areas.
Uses historical data to provide personalized learning recommendations.
"""

import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)


class StudyOptimizer:
    """
    Analyzes study patterns to optimize learning efficiency.
    
    Features:
    - Optimal time detection (when user performs best)
    - Weak areas identification (problem patterns)
    - Study session recommendations
    - Forgetting curve predictions
    """
    
    def __init__(self, db_manager=None):
        self.db = db_manager
        self._hour_performance = defaultdict(lambda: {'total': 0, 'correct': 0})
        self._day_performance = defaultdict(lambda: {'total': 0, 'correct': 0})
        self._category_performance = defaultdict(lambda: {'total': 0, 'correct': 0})
        self._recent_sessions = []
    
    def record_session(self, session_data: Dict):
        """
        Record a study session for analysis.
        
        Args:
            session_data: dict with hour, day_of_week, correct, total, 
                         session_type, categories
        """
        hour = session_data.get('hour', datetime.now().hour)
        day = session_data.get('day_of_week', datetime.now().weekday())
        correct = session_data.get('correct', 0)
        total = session_data.get('total', 0)
        categories = session_data.get('categories', ['general'])
        
        # Update hour performance
        self._hour_performance[hour]['total'] += total
        self._hour_performance[hour]['correct'] += correct
        
        # Update day performance
        self._day_performance[day]['total'] += total
        self._day_performance[day]['correct'] += correct
        
        # Update category performance
        for cat in categories:
            self._category_performance[cat]['total'] += total
            self._category_performance[cat]['correct'] += correct
        
        # Store session
        self._recent_sessions.append({
            'timestamp': datetime.now(),
            **session_data
        })
        
        # Keep only last 100 sessions in memory
        if len(self._recent_sessions) > 100:
            self._recent_sessions = self._recent_sessions[-100:]
    
    def get_optimal_study_hours(self, top_n: int = 3) -> List[Dict]:
        """
        Find the hours when user performs best.
        
        Returns:
            List of dicts with hour, accuracy, description
        """
        hour_stats = []
        
        for hour, data in self._hour_performance.items():
            if data['total'] >= 10:  # Minimum sample size
                accuracy = data['correct'] / data['total']
                hour_stats.append({
                    'hour': hour,
                    'accuracy': round(accuracy * 100, 1),
                    'sample_size': data['total'],
                    'time_label': self._format_hour(hour),
                })
        
        # Sort by accuracy
        hour_stats.sort(key=lambda x: x['accuracy'], reverse=True)
        
        # Add recommendations
        for stat in hour_stats[:top_n]:
            stat['recommendation'] = self._hour_recommendation(stat['hour'], stat['accuracy'])
        
        return hour_stats[:top_n]
    
    def get_optimal_days(self) -> List[Dict]:
        """
        Find the days when user performs best.
        
        Returns:
            List of dicts with day, accuracy
        """
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 
                     'Friday', 'Saturday', 'Sunday']
        day_stats = []
        
        for day, data in self._day_performance.items():
            if data['total'] >= 5:
                accuracy = data['correct'] / data['total']
                day_stats.append({
                    'day': day,
                    'day_name': day_names[day],
                    'accuracy': round(accuracy * 100, 1),
                    'sample_size': data['total'],
                })
        
        day_stats.sort(key=lambda x: x['accuracy'], reverse=True)
        return day_stats
    
    def identify_weak_areas(self) -> List[Dict]:
        """
        Identify categories where user struggles most.
        Feature 25: Weak Areas Identifier
        
        Returns:
            List of weak areas with recommendations
        """
        weak_areas = []
        
        for category, data in self._category_performance.items():
            if data['total'] >= 10:
                accuracy = data['correct'] / data['total']
                if accuracy < 0.7:  # Below 70% is considered weak
                    weak_areas.append({
                        'category': category,
                        'accuracy': round(accuracy * 100, 1),
                        'times_practiced': data['total'],
                        'severity': self._classify_weakness(accuracy),
                        'recommendation': self._weakness_recommendation(category, accuracy),
                    })
        
        # Sort by severity (lowest accuracy first)
        weak_areas.sort(key=lambda x: x['accuracy'])
        
        return weak_areas
    
    def predict_retention(self, word_data: Dict) -> Dict:
        """
        Predict retention percentage based on forgetting curve.
        Feature 8: Forgetting Curve Predictor
        
        Args:
            word_data: dict with last_review, repetitions, ease_factor
        
        Returns:
            dict with predicted_retention, days_until_next_review, confidence
        """
        last_review = word_data.get('last_review')
        repetitions = word_data.get('repetitions', 0)
        ease_factor = word_data.get('ease_factor', 2.5)
        
        if not last_review:
            return {
                'predicted_retention': 0,
                'status': 'never_reviewed',
                'recommendation': 'Start reviewing this word today!',
            }
        
        # Calculate days since last review
        if isinstance(last_review, str):
            last_review = datetime.fromisoformat(last_review)
        days_elapsed = (datetime.now() - last_review).days
        
        # Ebbinghaus forgetting curve approximation
        # R = e^(-t/S) where S is stability based on repetitions
        import math
        stability = (1 + repetitions) * ease_factor * 2
        retention = math.exp(-days_elapsed / stability)
        retention = max(0, min(1, retention))  # Clamp 0-1
        
        # Determine status
        if retention > 0.9:
            status = 'fresh'
            color = 'green'
        elif retention > 0.7:
            status = 'stable'
            color = 'green'
        elif retention > 0.5:
            status = 'fading'
            color = 'yellow'
        elif retention > 0.3:
            status = 'weak'
            color = 'orange'
        else:
            status = 'critical'
            color = 'red'
        
        # Calculate optimal review time
        target_retention = 0.9
        optimal_days = int(-stability * math.log(target_retention))
        days_until_review = max(0, optimal_days - days_elapsed)
        
        return {
            'predicted_retention': round(retention * 100, 1),
            'days_elapsed': days_elapsed,
            'status': status,
            'color': color,
            'days_until_review': days_until_review,
            'optimal_interval': optimal_days,
            'confidence': 'high' if repetitions >= 3 else 'medium' if repetitions >= 1 else 'low',
        }
    
    def get_study_recommendation(self) -> Dict:
        """
        Generate personalized study recommendations.
        
        Returns:
            dict with recommended_time, focus_areas, session_length, tips
        """
        optimal_hours = self.get_optimal_study_hours(1)
        weak_areas = self.identify_weak_areas()
        
        # Get current time context
        current_hour = datetime.now().hour
        
        recommendation = {
            'current_hour': current_hour,
            'is_optimal_time': False,
            'suggested_activities': [],
            'session_length_minutes': 25,  # Default Pomodoro
            'tips': [],
        }
        
        # Check if now is a good time
        if optimal_hours:
            best_hour = optimal_hours[0]['hour']
            hours_until_best = (best_hour - current_hour) % 24
            recommendation['best_hour'] = best_hour
            recommendation['hours_until_best'] = hours_until_best
            
            if abs(current_hour - best_hour) <= 1:
                recommendation['is_optimal_time'] = True
                recommendation['tips'].append(
                    f"🎯 This is your peak performance time! Make the most of it."
                )
        
        # Add focus area recommendations
        if weak_areas:
            weakest = weak_areas[0]
            recommendation['priority_area'] = weakest['category']
            recommendation['suggested_activities'].append({
                'activity': f"Review {weakest['category']} vocabulary",
                'reason': f"Your accuracy is {weakest['accuracy']}% - needs attention",
                'time': 15,
            })
        
        # Add balanced activities
        recommendation['suggested_activities'].extend([
            {'activity': 'Flashcard review', 'reason': 'Maintain existing knowledge', 'time': 10},
            {'activity': 'Learn new words', 'reason': 'Expand vocabulary', 'time': 10},
            {'activity': 'Listening practice', 'reason': 'Improve comprehension', 'time': 10},
        ])
        
        # Add time-based tips
        if 5 <= current_hour < 9:
            recommendation['tips'].append(
                "☀️ Morning study! Your brain is fresh - great for new material."
            )
        elif 12 <= current_hour < 14:
            recommendation['tips'].append(
                "🌤️ Post-lunch dip - keep sessions short and active."
            )
        elif 20 <= current_hour < 23:
            recommendation['tips'].append(
                "🌙 Evening study - good for review, avoid heavy new material."
            )
        
        return recommendation
    
    def _format_hour(self, hour: int) -> str:
        """Format hour for display."""
        if hour == 0:
            return "12:00 AM (Midnight)"
        elif hour < 12:
            return f"{hour}:00 AM"
        elif hour == 12:
            return "12:00 PM (Noon)"
        else:
            return f"{hour - 12}:00 PM"
    
    def _hour_recommendation(self, hour: int, accuracy: float) -> str:
        """Generate recommendation based on hour performance."""
        time_label = self._format_hour(hour)
        if accuracy >= 85:
            return f"Excellent performance at {time_label}! Schedule important reviews here."
        elif accuracy >= 70:
            return f"Good performance at {time_label}. Suitable for regular practice."
        else:
            return f"Variable performance at {time_label}. Consider changing study times."
    
    def _classify_weakness(self, accuracy: float) -> str:
        """Classify weakness severity."""
        if accuracy < 0.4:
            return 'severe'
        elif accuracy < 0.5:
            return 'significant'
        elif accuracy < 0.6:
            return 'moderate'
        else:
            return 'mild'
    
    def _weakness_recommendation(self, category: str, accuracy: float) -> str:
        """Generate recommendation for weak area."""
        if accuracy < 0.4:
            return f"Focus heavily on {category}. Consider learning fundamentals again."
        elif accuracy < 0.5:
            return f"Dedicate extra time to {category}. Use mnemonics and more context."
        elif accuracy < 0.6:
            return f"Increase practice frequency for {category}. Review mistakes carefully."
        else:
            return f"Keep practicing {category}. You're close to mastery!"
    
    def calculate_interleaving_benefit(self) -> Dict:
        """
        Feature 30: Determine if interleaved practice should be enabled.
        
        Interleaving mixes different categories during review, which
        improves long-term retention but feels harder short-term.
        """
        total_categories = len(self._category_performance)
        avg_accuracy = 0
        
        if self._category_performance:
            accuracies = []
            for data in self._category_performance.values():
                if data['total'] > 0:
                    accuracies.append(data['correct'] / data['total'])
            if accuracies:
                avg_accuracy = sum(accuracies) / len(accuracies)
        
        # Recommend interleaving if:
        # 1. User has multiple categories
        # 2. Average accuracy is above 60% (can handle the challenge)
        should_interleave = total_categories >= 3 and avg_accuracy >= 0.6
        
        return {
            'should_interleave': should_interleave,
            'total_categories': total_categories,
            'average_accuracy': round(avg_accuracy * 100, 1),
            'explanation': (
                "Interleaved practice mixes different word categories together. "
                "It feels harder but leads to better long-term retention. "
                "Recommended when you have good basics across multiple categories."
            ),
            'recommendation': (
                "Enable interleaved practice for deeper learning!" if should_interleave
                else "Build stronger foundations first before enabling interleaved mode."
            ),
        }


# Singleton instance
study_optimizer = StudyOptimizer()
