import re
import logging
from typing import Dict, List, Optional, Tuple
from openai import AsyncOpenAI
from config import OPENAI_API_KEY
import os
from pathlib import Path

# OpenAI client for tone analysis
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# Mood configuration
MOOD_CONFIG = {
    'happy': {
        'avatar': 'happy.png',
        'temperature': 0.85,
        'emoji': '😎',
        'keywords': ['лол', 'lol', 'хаха', 'haha', '😂', '😄', '😆', '🤣', 'весело', 'прикольно', 'круто', 'супер', 'топ', 'нічого собі'],
        'patterns': [r'[😀-😊😋-😎🤗🤩🥳]', r'ха+', r'лол+', r'хех+']
    },
    'sad': {
        'avatar': 'sad.png',
        'temperature': 0.25,
        'emoji': '😔',
        'keywords': ['чорт', 'блін', 'не можу', 'все пропало', 'помилка', 'не працює', 'не виходить', 'складно', 'важко', 'проблема'],
        'patterns': [r'[😢😭😞😔😟🙁☹️]', r'ох+', r'ай+', r'ну+']
    },
    'evil': {
        'avatar': 'evil.png',
        'temperature': 0.65,
        'emoji': '😈',
        'keywords': ['дурний', 'тупий', 'ідіот', 'фігня', 'лайно', 'треш', 'жах', 'кошмар', 'сарказм', 'іронія'],
        'patterns': [r'[😈👿😡🤬😠]', r'бл+я+', r'пі+ц+', r'сука+']
    },
    'neutral': {
        'avatar': 'neutral.png',
        'temperature': 0.55,
        'emoji': '🤖',
        'keywords': ['функція', 'клас', 'метод', 'API', 'база даних', 'код', 'програма', 'алгоритм', 'система'],
        'patterns': []
    }
}

class MoodManager:
    def __init__(self):
        self.current_mood = 'neutral'
        self.current_avatar = None
        self.message_history = []
        self.avatar_cache = {}
        
    def _analyze_keywords(self, text: str) -> Dict[str, int]:
        """Analyze text using keyword matching"""
        text_lower = text.lower()
        scores = {'happy': 0, 'sad': 0, 'evil': 0, 'neutral': 0}
        
        for mood, config in MOOD_CONFIG.items():
            # Check keywords
            for keyword in config['keywords']:
                if keyword in text_lower:
                    scores[mood] += 1
                    
            # Check patterns
            for pattern in config['patterns']:
                if re.search(pattern, text, re.IGNORECASE):
                    scores[mood] += 2
                    
        return scores
    
    async def _analyze_tone_with_ai(self, messages: List[str]) -> str:
        """Analyze tone using OpenAI for more sophisticated detection"""
        if not messages:
            return 'neutral'
            
        try:
            # Combine recent messages for context
            combined_text = ' '.join(messages[-3:])  # Last 3 messages
            
            system_prompt = """
            Analyze the tone and emotional state of the following messages. 
            Respond with exactly one word from: happy, sad, evil, neutral
            
            - happy: cheerful, playful, joking, positive emotions
            - sad: melancholic, confused, frustrated, disappointed
            - evil: sarcastic, angry, aggressive, dark humor
            - neutral: factual, technical, dry, professional
            """
            
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": combined_text}
                ],
                temperature=0.1,
                max_tokens=10
            )
            
            detected_mood = response.choices[0].message.content.strip().lower()
            
            # Validate response
            if detected_mood in MOOD_CONFIG:
                return detected_mood
            else:
                return 'neutral'
                
        except Exception as e:
            logging.error(f"[MOOD_MANAGER] AI tone analysis failed: {e}")
            return 'neutral'
    
    def detect_mood(self, text: str, use_ai: bool = True) -> str:
        """Detect mood from text using combined approach"""
        if not text:
            return 'neutral'
            
        # Add to message history
        self.message_history.append(text)
        self.message_history = self.message_history[-5:]  # Keep last 5 messages
        
        # Keyword-based analysis
        keyword_scores = self._analyze_keywords(text)
        
        # Find highest scoring mood
        best_mood = max(keyword_scores, key=keyword_scores.get)
        
        # If no clear winner or using AI, fall back to AI analysis
        if keyword_scores[best_mood] == 0 and use_ai:
            # Return a coroutine that needs to be awaited
            return self._analyze_tone_with_ai(self.message_history)
        
        return best_mood if keyword_scores[best_mood] > 0 else 'neutral'
    
    async def update_mood(self, text: str, use_ai: bool = True) -> Tuple[str, float, str]:
        """Update mood and return mood, temperature, and emoji"""
        detected_mood = self.detect_mood(text, use_ai)
        
        # If detect_mood returned a coroutine, await it
        if hasattr(detected_mood, '__await__'):
            detected_mood = await detected_mood
            
        self.current_mood = detected_mood
        config = MOOD_CONFIG[detected_mood]
        
        logging.info(f"[MOOD_MANAGER] Updated mood to: {detected_mood}")
        
        return detected_mood, config['temperature'], config['emoji']
    
    def get_status_prefix(self, mood: str, temperature: float) -> str:
        """Generate status prefix for responses"""
        emoji = MOOD_CONFIG[mood]['emoji']
        temp_emoji = self._get_temperature_emoji(temperature)
        
        return f"[🤖 Status: {mood.capitalize()} {emoji} | {temp_emoji} Temp: {temperature:.2f}]"
    
    def _get_temperature_emoji(self, temperature: float) -> str:
        """Get emoji based on temperature"""
        if temperature >= 0.8:
            return "🔥"
        elif temperature >= 0.6:
            return "🌡️"
        elif temperature >= 0.4:
            return "❄️"
        else:
            return "🧊"
    
    def get_mood_image_path(self, mood: str) -> str:
        """Get path to mood image file"""
        return f"data/bot_status/{MOOD_CONFIG[mood]['avatar']}"
    
    def mood_image_exists(self, mood: str) -> bool:
        """Check if mood image exists"""
        image_path = self.get_mood_image_path(mood)
        exists = os.path.exists(image_path)
        if not exists:
            logging.error(f"[MOOD_MANAGER] Mood image not found: {image_path}")
        return exists
    
    def get_current_mood(self) -> str:
        """Get current mood"""
        return self.current_mood
    
    def get_temperature(self, mood: str = None) -> float:
        """Get temperature for specified mood or current mood"""
        if mood is None:
            mood = self.current_mood
        return MOOD_CONFIG[mood]['temperature']
    
    def reset_mood(self):
        """Reset mood to neutral"""
        self.current_mood = 'neutral'
        self.current_avatar = None
        self.message_history = []
        logging.info("[MOOD_MANAGER] Mood reset to neutral")
    
