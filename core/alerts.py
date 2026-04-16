"""
Alert Manager
Handle and route system alerts
"""

import logging
from typing import Dict, Any, List
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertManager:
    """Manage and route system alerts"""
    
    def __init__(self):
        self.alerts: List[Dict] = []
        self.handlers = {
            AlertLevel.INFO: [],
            AlertLevel.WARNING: [],
            AlertLevel.ERROR: [],
            AlertLevel.CRITICAL: []
        }
        
    def register_handler(self, level: AlertLevel, handler):
        """Register alert handler"""
        self.handlers[level].append(handler)
        
    def send_alert(self, level: AlertLevel, message: str, 
                   source: str = "system", metadata: Dict = None):
        """Send alert"""
        alert = {
            'id': len(self.alerts) + 1,
            'timestamp': datetime.utcnow().isoformat(),
            'level': level.value,
            'message': message,
            'source': source,
            'metadata': metadata or {}
        }
        
        self.alerts.append(alert)
        
        # Log alert
        if level == AlertLevel.CRITICAL:
            logger.critical(f"[{source}] {message}")
        elif level == AlertLevel.ERROR:
            logger.error(f"[{source}] {message}")
        elif level == AlertLevel.WARNING:
            logger.warning(f"[{source}] {message}")
        else:
            logger.info(f"[{source}] {message}")
        
        # Call handlers
        for handler in self.handlers.get(level, []):
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Alert handler error: {e}")
        
        # Keep only last 1000 alerts
        if len(self.alerts) > 1000:
            self.alerts = self.alerts[-1000:]
            
    def get_recent_alerts(self, level: AlertLevel = None, limit: int = 100) -> List[Dict]:
        """Get recent alerts"""
        filtered = self.alerts
        
        if level:
            filtered = [a for a in filtered if a['level'] == level.value]
        
        return filtered[-limit:]
        
    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts = []
