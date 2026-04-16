"""
News & Sentiment Strategy
Trade based on real-time news and sentiment analysis
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class NewsSentimentStrategy:
    """
    News & Sentiment Trading Strategy
    
    Enters positions based on:
    - Real-time news sentiment
    - Economic data releases
    - Social media sentiment
    - Unexpected events
    
    Requires fast reaction and careful risk management.
    """
    
    def __init__(self):
        self.sentiment_threshold = 0.6  # Minimum sentiment score
        self.news_lookback_minutes = 30
        self.impact_cooldown_hours = 4  # Avoid trading same event twice
        
        # Track processed events
        self.processed_events = set()
        
    def evaluate(self, market: str, symbol: str, data: Dict,
                 position: Optional[Dict], context: Dict = None) -> Optional[Dict]:
        """Evaluate news/sentiment opportunity"""
        try:
            # Get news/sentiment data
            news_data = data.get('news', [])
            sentiment = data.get('sentiment', {})
            economic_events = data.get('economic_events', [])
            
            # Check for high-impact economic events
            if economic_events:
                for event in economic_events:
                    if self._is_high_impact(event):
                        result = self._evaluate_economic_event(event, market, symbol)
                        if result:
                            return result
            
            # Check news sentiment
            if sentiment:
                overall_sentiment = sentiment.get('overall', 0)
                sentiment_confidence = sentiment.get('confidence', 0)
                
                if abs(overall_sentiment) > self.sentiment_threshold and sentiment_confidence > 0.7:
                    return self._build_sentiment_signal(
                        overall_sentiment, sentiment_confidence, 
                        sentiment.get('sources', []), market, symbol
                    )
            
            # Check recent news
            if news_data:
                recent_news = self._filter_recent_news(news_data)
                if recent_news:
                    return self._evaluate_news_cluster(recent_news, market, symbol)
            
            return None
            
        except Exception as e:
            logger.error(f"Error in news sentiment strategy: {e}")
            return None
    
    def _is_high_impact(self, event: Dict) -> bool:
        """Check if economic event is high impact"""
        # High impact events
        high_impact_events = [
            'FOMC', 'Fed', 'NFP', 'CPI', 'GDP', 'Unemployment',
            'Interest Rate', 'ECB', 'BOE', 'BOJ'
        ]
        
        event_title = event.get('title', '').upper()
        
        # Check if already processed
        event_id = event.get('id', event_title)
        if event_id in self.processed_events:
            return False
        
        # Check impact level
        if event.get('impact') == 'high':
            return True
        
        # Check for high-impact keywords
        for keyword in high_impact_events:
            if keyword in event_title:
                return True
        
        return False
    
    def _evaluate_economic_event(self, event: Dict, market: str, symbol: str) -> Optional[Dict]:
        """Evaluate economic event for trading signal"""
        event_title = event.get('title', '')
        actual = event.get('actual')
        forecast = event.get('forecast')
        previous = event.get('previous')
        
        # Mark as processed
        self.processed_events.add(event.get('id', event_title))
        
        # Determine bullish/bearish based on event type and deviation
        if 'CPI' in event_title.upper() or 'Inflation' in event_title:
            # Higher CPI = bearish for risk assets
            if actual and forecast:
                if actual > forecast * 1.001:  # Higher than expected
                    action = 'sell'
                    confidence = min(abs(actual - forecast) / forecast * 10, 0.9)
                    reasoning = f"CPI higher than expected: {actual} vs {forecast} forecast. Inflationary pressure."
                else:
                    action = 'buy'
                    confidence = min(abs(actual - forecast) / forecast * 10, 0.9)
                    reasoning = f"CPI lower than expected: {actual} vs {forecast} forecast. Inflation cooling."
            else:
                return None
                
        elif 'NFP' in event_title.upper() or 'Non-Farm' in event_title:
            # Strong jobs = bullish USD, mixed for risk
            if actual and forecast:
                if actual > forecast:
                    action = 'buy'  # Bullish USD assets
                    confidence = 0.75
                    reasoning = f"Strong NFP: {actual}K vs {forecast}K expected."
                else:
                    action = 'sell'
                    confidence = 0.75
                    reasoning = f"Weak NFP: {actual}K vs {forecast}K expected."
            else:
                return None
                
        elif 'FOMC' in event_title.upper() or 'Fed' in event_title:
            # Hawkish = bearish risk, Dovish = bullish
            if 'Hawkish' in event.get('sentiment', ''):
                action = 'sell'
                confidence = 0.8
                reasoning = "FOMC hawkish tone. Rate hike expectations."
            elif 'Dovish' in event.get('sentiment', ''):
                action = 'buy'
                confidence = 0.8
                reasoning = "FOMC dovish tone. Rate cut expectations."
            else:
                return None
        else:
            # Generic event handling
            if actual and forecast and previous:
                deviation = (actual - forecast) / forecast
                if abs(deviation) > 0.01:  # 1% deviation
                    action = 'buy' if deviation > 0 else 'sell'
                    confidence = min(abs(deviation) * 5, 0.8)
                    reasoning = f"{event_title}: {actual} vs {forecast} expected ({deviation:+.2%})"
                else:
                    return None
            else:
                return None
        
        return {
            'strategy_name': 'news_sentiment',
            'action': action,
            'confidence': confidence,
            'reasoning': reasoning,
            'indicators': {
                'event_type': 'economic',
                'event_title': event_title,
                'actual': actual,
                'forecast': forecast,
                'impact': 'high'
            }
        }
    
    def _build_sentiment_signal(self, sentiment: float, confidence: float,
                                sources: list, market: str, symbol: str) -> Dict:
        """Build signal from sentiment analysis"""
        if sentiment > 0:
            action = 'buy'
            sentiment_desc = 'positive'
        else:
            action = 'sell'
            sentiment_desc = 'negative'
        
        reasoning = f"{sentiment_desc.title()} sentiment detected ({sentiment:.2f}) from {len(sources)} sources. "
        reasoning += f"Confidence: {confidence:.0%}."
        
        return {
            'strategy_name': 'news_sentiment',
            'action': action,
            'confidence': confidence * abs(sentiment),
            'reasoning': reasoning,
            'indicators': {
                'sentiment_score': sentiment,
                'sentiment_confidence': confidence,
                'sources': sources,
                'event_type': 'sentiment'
            }
        }
    
    def _filter_recent_news(self, news: list) -> list:
        """Filter news to last 30 minutes"""
        cutoff = datetime.utcnow() - timedelta(minutes=self.news_lookback_minutes)
        recent = []
        
        for item in news:
            pub_time = item.get('published')
            if pub_time:
                if isinstance(pub_time, str):
                    pub_time = datetime.fromisoformat(pub_time.replace('Z', '+00:00'))
                if pub_time > cutoff:
                    recent.append(item)
        
        return recent
    
    def _evaluate_news_cluster(self, news: list, market: str, symbol: str) -> Optional[Dict]:
        """Evaluate cluster of recent news"""
        if len(news) < 2:
            return None
        
        # Simple sentiment aggregation
        bullish_keywords = ['bullish', 'rally', 'surge', 'moon', 'breakout', 'adoption']
        bearish_keywords = ['bearish', 'crash', 'dump', 'scam', 'hack', 'ban', 'regulation']
        
        bullish_count = 0
        bearish_count = 0
        
        for item in news:
            title = item.get('title', '').lower()
            
            for keyword in bullish_keywords:
                if keyword in title:
                    bullish_count += 1
                    break
            
            for keyword in bearish_keywords:
                if keyword in title:
                    bearish_count += 1
                    break
        
        total = bullish_count + bearish_count
        if total < 2:
            return None
        
        if bullish_count > bearish_count * 1.5:
            action = 'buy'
            confidence = min(bullish_count / total, 0.8)
            reasoning = f"News cluster bullish: {bullish_count} bullish vs {bearish_count} bearish articles."
        elif bearish_count > bullish_count * 1.5:
            action = 'sell'
            confidence = min(bearish_count / total, 0.8)
            reasoning = f"News cluster bearish: {bearish_count} bearish vs {bullish_count} bullish articles."
        else:
            return None
        
        return {
            'strategy_name': 'news_sentiment',
            'action': action,
            'confidence': confidence,
            'reasoning': reasoning,
            'indicators': {
                'bullish_articles': bullish_count,
                'bearish_articles': bearish_count,
                'event_type': 'news_cluster'
            }
        }
    
    def cleanup_old_events(self):
        """Remove old events from processed set"""
        # Keep only recent events
        cutoff = datetime.utcnow() - timedelta(hours=24)
        # In practice, would store timestamps with events
        pass
