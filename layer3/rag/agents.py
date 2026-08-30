"""
RAG Agents — Layer 3 v5.0 §6

Central Bank RAG Engine:
- Fed sentiment extraction
- BoJ sentiment extraction
- Sentiment classification
- Expectation gap calculation
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime
import re


@dataclass
class RagSignal:
    """RAG signal from central bank communication."""
    source: str           # "Fed" | "BoJ"
    sentiment_score: float  # -1 (Dovish) to +1 (Hawkish)
    expectation_gap: float  # Actual vs. expected sentiment
    key_quotes: List[str]
    summary: str
    timestamp: str
    document_publication_time: str
    available_time: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'source': self.source,
            'sentiment': self.sentiment_score,
            'expectation_gap': self.expectation_gap,
            'key_quotes': self.key_quotes,
            'summary': self.summary,
            'timestamp': self.timestamp,
            'document_publication_time': self.document_publication_time,
            'available_time': self.available_time
        }


class CentralBankRAGEngine:
    """
    Central Bank RAG Engine.
    
    Extracts actionable intelligence from central bank communications.
    """
    
    def __init__(self):
        self.hawkish_terms = [
            'tighten', 'restrictive', 'higher rates', 'inflation risks',
            'overheating', 'upside risks', 'vigilant', 'persistent'
        ]
        self.dovish_terms = [
            'accommodative', 'support', 'downside risks', 'patient',
            'gradual', 'carefully', 'uncertain', 'transitory'
        ]
    
    def _extract_sentiment(self, text: str) -> float:
        """
        Extract sentiment score from text.
        Scoring: Hawkish terms: +1 each, Dovish terms: -1 each
        Normalize to range [-1, +1]
        """
        text_lower = text.lower()
        
        hawkish_count = sum(1 for term in self.hawkish_terms if term in text_lower)
        dovish_count = sum(1 for term in self.dovish_terms if term in text_lower)
        
        total = hawkish_count + dovish_count
        if total == 0:
            return 0.0
        
        score = (hawkish_count - dovish_count) / total
        return max(-1.0, min(1.0, score))
    
    def _extract_key_quotes(self, text: str, max_quotes: int = 3) -> List[str]:
        """Extract key quotes from text."""
        # Simple extract: sentences with key terms
        sentences = re.split(r'[.!?]+', text)
        key_quotes = []
        
        for sentence in sentences:
            if any(term in sentence.lower() for term in self.hawkish_terms + self.dovish_terms):
                if len(sentence.strip()) > 20:
                    key_quotes.append(sentence.strip())
                    if len(key_quotes) >= max_quotes:
                        break
        
        return key_quotes
    
    def _generate_summary(self, text: str, sentiment: float) -> str:
        """Generate summary of communication."""
        if sentiment > 0.3:
            bias = "hawkish"
        elif sentiment < -0.3:
            bias = "dovish"
        else:
            bias = "neutral"
        
        # Extract first 100 chars for summary
        summary = text[:100] + "..." if len(text) > 100 else text
        return f"Communication shows {bias} bias: {summary}"
    
    def process_fed(self, text: str, expected_sentiment: float = 0.0,
                   publication_time: str = None) -> RagSignal:
        """
        Process Federal Reserve communication.
        
        §6.1: FOMC statements, press conferences, meeting minutes
        """
        sentiment = self._extract_sentiment(text)
        expectation_gap = sentiment - expected_sentiment
        
        return RagSignal(
            source="Fed",
            sentiment_score=sentiment,
            expectation_gap=expectation_gap,
            key_quotes=self._extract_key_quotes(text),
            summary=self._generate_summary(text, sentiment),
            timestamp=datetime.now().isoformat(),
            document_publication_time=publication_time or datetime.now().isoformat(),
            available_time=datetime.now().isoformat()
        )
    
    def process_boj(self, text: str, expected_sentiment: float = 0.0,
                   publication_time: str = None) -> RagSignal:
        """
        Process Bank of Japan communication.
        
        §6.1: Policy statements, press conferences, outlook report
        """
        sentiment = self._extract_sentiment(text)
        expectation_gap = sentiment - expected_sentiment
        
        return RagSignal(
            source="BoJ",
            sentiment_score=sentiment,
            expectation_gap=expectation_gap,
            key_quotes=self._extract_key_quotes(text),
            summary=self._generate_summary(text, sentiment),
            timestamp=datetime.now().isoformat(),
            document_publication_time=publication_time or datetime.now().isoformat(),
            available_time=datetime.now().isoformat()
        )
    
    def get_features(self, fed_signal: RagSignal, boj_signal: RagSignal) -> Dict[str, float]:
        """
        Get RAG features for model input.
        
        §6.3: RAG outputs as features
        """
        return {
            'fed_sentiment_score': fed_signal.sentiment_score,
            'boj_sentiment_score': boj_signal.sentiment_score,
            'fed_expectation_gap': fed_signal.expectation_gap,
            'boj_expectation_gap': boj_signal.expectation_gap,
            'fed_hawkish_shift': fed_signal.sentiment_score,  # Simplified
            'boj_dovish_shift': -boj_signal.sentiment_score,  # Simplified
            'fed_rate_path_bias': fed_signal.sentiment_score * 0.5,
            'boj_rate_path_bias': boj_signal.sentiment_score * 0.5
        }
