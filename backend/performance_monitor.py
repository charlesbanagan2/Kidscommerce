# ⚡ REAL-TIME PERFORMANCE MONITOR
# Tracks all API endpoints and database queries

import time
from functools import wraps
from flask import request, g
import logging

# Performance thresholds (in seconds)
SLOW_REQUEST_THRESHOLD = 0.5  # 500ms
VERY_SLOW_REQUEST_THRESHOLD = 1.0  # 1 second

# Setup logging
logging.basicConfig(
    filename='performance.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            'total_requests': 0,
            'slow_requests': 0,
            'very_slow_requests': 0,
            'total_time': 0,
            'endpoints': {}
        }
    
    def track_request(self, endpoint, duration, query_count=0):
        """Track request performance"""
        self.metrics['total_requests'] += 1
        self.metrics['total_time'] += duration
        
        if duration > VERY_SLOW_REQUEST_THRESHOLD:
            self.metrics['very_slow_requests'] += 1
            logging.warning(f"VERY SLOW: {endpoint} took {duration:.3f}s with {query_count} queries")
        elif duration > SLOW_REQUEST_THRESHOLD:
            self.metrics['slow_requests'] += 1
            logging.info(f"SLOW: {endpoint} took {duration:.3f}s with {query_count} queries")
        
        # Track per-endpoint metrics
        if endpoint not in self.metrics['endpoints']:
            self.metrics['endpoints'][endpoint] = {
                'count': 0,
                'total_time': 0,
                'min_time': float('inf'),
                'max_time': 0,
                'slow_count': 0
            }
        
        ep_metrics = self.metrics['endpoints'][endpoint]
        ep_metrics['count'] += 1
        ep_metrics['total_time'] += duration
        ep_metrics['min_time'] = min(ep_metrics['min_time'], duration)
        ep_metrics['max_time'] = max(ep_metrics['max_time'], duration)
        
        if duration > SLOW_REQUEST_THRESHOLD:
            ep_metrics['slow_count'] += 1
    
    def get_stats(self):
        """Get performance statistics"""
        stats = {
            'total_requests': self.metrics['total_requests'],
            'slow_requests': self.metrics['slow_requests'],
            'very_slow_requests': self.metrics['very_slow_requests'],
            'avg_response_time': self.metrics['total_time'] / max(1, self.metrics['total_requests']),
            'endpoints': []
        }
        
        # Sort endpoints by average time (slowest first)
        for endpoint, metrics in self.metrics['endpoints'].items():
            avg_time = metrics['total_time'] / max(1, metrics['count'])
            stats['endpoints'].append({
                'endpoint': endpoint,
                'count': metrics['count'],
                'avg_time': avg_time,
                'min_time': metrics['min_time'],
                'max_time': metrics['max_time'],
                'slow_count': metrics['slow_count']
            })
        
        stats['endpoints'].sort(key=lambda x: x['avg_time'], reverse=True)
        return stats

# Global monitor instance
monitor = PerformanceMonitor()

def track_performance(f):
    """Decorator to track endpoint performance"""
    @wraps(f)
    def decorated(*args, **kwargs):
        start_time = time.time()
        
        # Track query count
        g.query_count = 0
        
        try:
            result = f(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            query_count = getattr(g, 'query_count', 0)
            
            endpoint = request.endpoint or 'unknown'
            monitor.track_request(endpoint, duration, query_count)
    
    return decorated
