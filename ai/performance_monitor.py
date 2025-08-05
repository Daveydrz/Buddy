"""
Performance Monitor for Buddy System
Created: 2025-08-05
Purpose: Track response times, detect performance issues, and provide metrics
"""

import time
import threading
import json
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import deque, defaultdict
from enum import Enum

class PerformanceLevel(Enum):
    EXCELLENT = "excellent"    # < 2 seconds
    GOOD = "good"             # 2-5 seconds
    ACCEPTABLE = "acceptable"  # 5-10 seconds
    SLOW = "slow"             # 10-30 seconds
    CRITICAL = "critical"     # > 30 seconds

@dataclass
class PerformanceMetric:
    """Single performance measurement"""
    timestamp: float
    operation: str
    duration: float
    status: str = "success"
    error: Optional[str] = None
    context: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def get_performance_level(self) -> PerformanceLevel:
        """Classify performance level based on duration"""
        if self.duration < 2.0:
            return PerformanceLevel.EXCELLENT
        elif self.duration < 5.0:
            return PerformanceLevel.GOOD
        elif self.duration < 10.0:
            return PerformanceLevel.ACCEPTABLE
        elif self.duration < 30.0:
            return PerformanceLevel.SLOW
        else:
            return PerformanceLevel.CRITICAL

class PerformanceMonitor:
    """Monitor and track system performance metrics"""
    
    def __init__(self, save_path: str = "performance_metrics.json", max_metrics: int = 1000):
        self.save_path = save_path
        self.max_metrics = max_metrics
        self.metrics: deque = deque(maxlen=max_metrics)
        self.operation_stats: Dict[str, Dict] = defaultdict(lambda: {
            'count': 0,
            'total_duration': 0.0,
            'min_duration': float('inf'),
            'max_duration': 0.0,
            'success_count': 0,
            'error_count': 0,
            'last_measurement': None
        })
        self.lock = threading.Lock()
        self.active_operations: Dict[str, float] = {}  # Track ongoing operations
        
        # Performance thresholds (configurable)
        self.thresholds = {
            'response_generation': 5.0,
            'consciousness_processing': 3.0,
            'memory_retrieval': 1.0,
            'llm_request': 10.0,
            'voice_recognition': 2.0
        }
        
        # Load existing metrics
        self._load_metrics()
        
        print("[PerformanceMonitor] ✅ Performance monitoring initialized")
    
    def start_operation(self, operation_id: str) -> str:
        """Start tracking an operation"""
        with self.lock:
            start_time = time.time()
            self.active_operations[operation_id] = start_time
            return operation_id
    
    def end_operation(self, operation_id: str, operation_name: str, status: str = "success", 
                     error: Optional[str] = None, context: Dict[str, Any] = None) -> PerformanceMetric:
        """End tracking an operation and record metric"""
        with self.lock:
            if operation_id not in self.active_operations:
                print(f"[PerformanceMonitor] ⚠️ Operation {operation_id} not found in active operations")
                return None
            
            start_time = self.active_operations.pop(operation_id)
            duration = time.time() - start_time
            
            metric = PerformanceMetric(
                timestamp=time.time(),
                operation=operation_name,
                duration=duration,
                status=status,
                error=error,
                context=context or {}
            )
            
            self.metrics.append(metric)
            self._update_operation_stats(metric)
            
            # Check for performance issues
            self._check_performance_threshold(metric)
            
            return metric
    
    def record_metric(self, operation_name: str, duration: float, status: str = "success",
                     error: Optional[str] = None, context: Dict[str, Any] = None) -> PerformanceMetric:
        """Record a metric directly (for operations not tracked with start/end)"""
        with self.lock:
            metric = PerformanceMetric(
                timestamp=time.time(),
                operation=operation_name,
                duration=duration,
                status=status,
                error=error,
                context=context or {}
            )
            
            self.metrics.append(metric)
            self._update_operation_stats(metric)
            self._check_performance_threshold(metric)
            
            return metric
    
    def _update_operation_stats(self, metric: PerformanceMetric):
        """Update statistics for an operation"""
        stats = self.operation_stats[metric.operation]
        stats['count'] += 1
        stats['total_duration'] += metric.duration
        stats['min_duration'] = min(stats['min_duration'], metric.duration)
        stats['max_duration'] = max(stats['max_duration'], metric.duration)
        stats['last_measurement'] = metric.timestamp
        
        if metric.status == "success":
            stats['success_count'] += 1
        else:
            stats['error_count'] += 1
    
    def _check_performance_threshold(self, metric: PerformanceMetric):
        """Check if operation exceeded performance threshold"""
        threshold = self.thresholds.get(metric.operation, 30.0)  # Default 30s threshold
        
        if metric.duration > threshold:
            level = metric.get_performance_level()
            print(f"[PerformanceMonitor] ⚠️ SLOW OPERATION: {metric.operation} took {metric.duration:.2f}s (threshold: {threshold}s) - {level.value}")
            
            # Log critical performance issues
            if level == PerformanceLevel.CRITICAL:
                self._log_critical_performance_issue(metric, threshold)
    
    def _log_critical_performance_issue(self, metric: PerformanceMetric, threshold: float):
        """Log critical performance issues to file"""
        try:
            log_entry = {
                'timestamp': datetime.fromtimestamp(metric.timestamp).isoformat(),
                'operation': metric.operation,
                'duration': metric.duration,
                'threshold': threshold,
                'status': metric.status,
                'error': metric.error,
                'context': metric.context
            }
            
            with open("critical_performance_issues.log", "a") as f:
                f.write(json.dumps(log_entry) + "\n")
                
        except Exception as e:
            print(f"[PerformanceMonitor] ❌ Failed to log critical issue: {e}")
    
    def get_operation_stats(self, operation_name: str) -> Dict[str, Any]:
        """Get statistics for a specific operation"""
        with self.lock:
            if operation_name not in self.operation_stats:
                return None
                
            stats = self.operation_stats[operation_name].copy()
            if stats['count'] > 0:
                stats['average_duration'] = stats['total_duration'] / stats['count']
                stats['success_rate'] = stats['success_count'] / stats['count']
            else:
                stats['average_duration'] = 0.0
                stats['success_rate'] = 0.0
                
            return stats
    
    def get_overall_stats(self) -> Dict[str, Any]:
        """Get overall performance statistics"""
        with self.lock:
            now = time.time()
            recent_metrics = [m for m in self.metrics if now - m.timestamp < 3600]  # Last hour
            
            if not recent_metrics:
                return {
                    'total_operations': 0,
                    'recent_operations': 0,
                    'average_response_time': 0.0,
                    'performance_distribution': {},
                    'error_rate': 0.0
                }
            
            total_duration = sum(m.duration for m in recent_metrics)
            error_count = sum(1 for m in recent_metrics if m.status != "success")
            
            # Performance level distribution
            distribution = defaultdict(int)
            for metric in recent_metrics:
                level = metric.get_performance_level()
                distribution[level.value] += 1
            
            return {
                'total_operations': len(self.metrics),
                'recent_operations': len(recent_metrics),
                'average_response_time': total_duration / len(recent_metrics),
                'performance_distribution': dict(distribution),
                'error_rate': error_count / len(recent_metrics),
                'active_operations': len(self.active_operations),
                'timestamp': now
            }
    
    def get_slow_operations(self, threshold: float = 10.0, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent slow operations"""
        with self.lock:
            slow_ops = [
                m.to_dict() for m in self.metrics 
                if m.duration > threshold
            ]
            # Sort by duration, descending
            slow_ops.sort(key=lambda x: x['duration'], reverse=True)
            return slow_ops[:limit]
    
    def save_metrics(self):
        """Save metrics to file"""
        try:
            with self.lock:
                data = {
                    'metrics': [m.to_dict() for m in list(self.metrics)],
                    'operation_stats': dict(self.operation_stats),
                    'thresholds': self.thresholds,
                    'timestamp': time.time()
                }
                
                with open(self.save_path, 'w') as f:
                    json.dump(data, f, indent=2)
                    
        except Exception as e:
            print(f"[PerformanceMonitor] ❌ Failed to save metrics: {e}")
    
    def _load_metrics(self):
        """Load metrics from file"""
        try:
            if os.path.exists(self.save_path):
                with open(self.save_path, 'r') as f:
                    data = json.load(f)
                
                # Load recent metrics (last 24 hours)
                cutoff_time = time.time() - 86400
                for metric_data in data.get('metrics', []):
                    if metric_data['timestamp'] > cutoff_time:
                        metric = PerformanceMetric(**metric_data)
                        self.metrics.append(metric)
                        self._update_operation_stats(metric)
                
                # Load thresholds
                self.thresholds.update(data.get('thresholds', {}))
                
                print(f"[PerformanceMonitor] ✅ Loaded {len(self.metrics)} recent metrics")
                
        except Exception as e:
            print(f"[PerformanceMonitor] ⚠️ Failed to load metrics: {e}")

# Context manager for easy operation tracking
class PerformanceTimer:
    """Context manager for tracking operation performance"""
    
    def __init__(self, monitor: PerformanceMonitor, operation_name: str, context: Dict[str, Any] = None):
        self.monitor = monitor
        self.operation_name = operation_name
        self.context = context or {}
        self.operation_id = None
        self.start_time = None
    
    def __enter__(self):
        self.operation_id = f"{self.operation_name}_{time.time()}"
        self.monitor.start_operation(self.operation_id)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        status = "success" if exc_type is None else "error"
        error = str(exc_val) if exc_val else None
        self.monitor.end_operation(self.operation_id, self.operation_name, status, error, self.context)

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

# Convenience function
def track_performance(operation_name: str, context: Dict[str, Any] = None):
    """Decorator or context manager for tracking performance"""
    return PerformanceTimer(performance_monitor, operation_name, context)

print("[PerformanceMonitor] ✅ Performance monitoring system ready")