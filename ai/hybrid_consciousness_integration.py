#!/usr/bin/env python3
"""
Hybrid Consciousness Integration Layer - Advanced Reactive Neural Coordination

This module provides the integration layer that coordinates:
1. Event-Driven Nervous System
2. Async Neural Pathways
3. Parallel Processing Cortex
4. Backpressure handling and system stability
5. Observability metrics and telemetry

Created: 2025-01-09
Purpose: Hybrid coordination of all reactive neural architecture components
"""

import asyncio
import threading
import time
import logging
import uuid
import weakref
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List, Callable, Optional, Tuple, Union, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import defaultdict, deque
from threading import RLock, Lock, Event
try:
    import psutil
except ImportError:
    psutil = None
import traceback
from contextlib import asynccontextmanager

# Helper to ensure an event loop exists
def _ensure_loop():
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop

# Import reactive components
from ai.reactive_neural_architecture import (
    EventBus, AsyncNeuralPathways, WorkStealingThreadPool, OptimizedMemoryManager,
    NeuralEvent, EventType, EventPriority, EventSubscriber
)

# Import existing parallel processor
from ai.parallel_processor import ParallelConsciousnessProcessor, ModuleConfig, ModuleResult, ModulePriority

logger = logging.getLogger(__name__)

class ProcessingMode(Enum):
    """Processing modes for the hybrid system"""
    REACTIVE_ONLY = auto()      # Event-driven only
    ASYNC_ONLY = auto()         # Async pathways only
    PARALLEL_ONLY = auto()      # Thread-based only
    HYBRID_BALANCED = auto()    # Balanced combination
    HYBRID_PERFORMANCE = auto() # Performance-optimized combination
    HYBRID_MEMORY = auto()      # Memory-optimized combination

class BackpressureState(Enum):
    """System backpressure states"""
    NORMAL = auto()
    ELEVATED = auto()
    HIGH = auto()
    CRITICAL = auto()

@dataclass
class HybridWorkload:
    """Workload definition for hybrid processing"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    text: str = ""
    user: str = ""
    processing_mode: ProcessingMode = ProcessingMode.HYBRID_BALANCED
    priority: EventPriority = EventPriority.MEDIUM
    timeout: float = 30.0
    context: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    
    # Performance requirements
    max_latency: float = 5.0
    min_throughput: float = 1.0
    memory_limit: int = 100 * 1024 * 1024  # 100MB
    
    # Failure handling
    retry_policy: Dict[str, Any] = field(default_factory=lambda: {
        'max_retries': 3,
        'backoff_multiplier': 2.0,
        'initial_delay': 1.0
    })

@dataclass
class ProcessingResult:
    """Result from hybrid consciousness processing"""
    workload_id: str
    success: bool
    result: Any
    processing_time: float
    mode_used: ProcessingMode
    resources_used: Dict[str, Any]
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class BackpressureManager:
    """Manages system backpressure and load balancing"""
    
    def __init__(self):
        self.current_state = BackpressureState.NORMAL
        self.state_lock = Lock()
        self.metrics = {
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'event_queue_depth': 0,
            'async_operations': 0,
            'thread_utilization': 0.0,
            'response_times': deque(maxlen=100)
        }
        self.thresholds = {
            BackpressureState.NORMAL: {'cpu': 50, 'memory': 60, 'queue': 100},
            BackpressureState.ELEVATED: {'cpu': 70, 'memory': 75, 'queue': 500},
            BackpressureState.HIGH: {'cpu': 85, 'memory': 85, 'queue': 1000},
            BackpressureState.CRITICAL: {'cpu': 95, 'memory': 95, 'queue': 2000}
        }
        
        # Start monitoring
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info("[BackpressureManager] 📊 Backpressure monitoring initialized")
    
    def _monitor_loop(self):
        """Continuous monitoring loop"""
        while self.monitoring_active:
            try:
                # Update metrics
                if psutil:
                    process = psutil.Process()
                    self.metrics['cpu_usage'] = process.cpu_percent()
                    self.metrics['memory_usage'] = process.memory_percent()
                else:
                    # Fallback values when psutil not available
                    self.metrics['cpu_usage'] = 10.0  # Conservative estimate
                    self.metrics['memory_usage'] = 20.0
                
                # Determine new state
                new_state = self._calculate_backpressure_state()
                
                with self.state_lock:
                    if new_state != self.current_state:
                        logger.info(f"[BackpressureManager] 📈 State change: {self.current_state.name} -> {new_state.name}")
                        self.current_state = new_state
                
                time.sleep(1.0)  # Monitor every second
                
            except Exception as e:
                logger.error(f"[BackpressureManager] ❌ Monitoring error: {e}")
                time.sleep(5.0)
    
    def _calculate_backpressure_state(self) -> BackpressureState:
        """Calculate current backpressure state"""
        cpu = self.metrics['cpu_usage']
        memory = self.metrics['memory_usage']
        queue = self.metrics['event_queue_depth']
        
        # Critical state
        if (cpu > self.thresholds[BackpressureState.CRITICAL]['cpu'] or
            memory > self.thresholds[BackpressureState.CRITICAL]['memory'] or
            queue > self.thresholds[BackpressureState.CRITICAL]['queue']):
            return BackpressureState.CRITICAL
        
        # High state
        if (cpu > self.thresholds[BackpressureState.HIGH]['cpu'] or
            memory > self.thresholds[BackpressureState.HIGH]['memory'] or
            queue > self.thresholds[BackpressureState.HIGH]['queue']):
            return BackpressureState.HIGH
        
        # Elevated state
        if (cpu > self.thresholds[BackpressureState.ELEVATED]['cpu'] or
            memory > self.thresholds[BackpressureState.ELEVATED]['memory'] or
            queue > self.thresholds[BackpressureState.ELEVATED]['queue']):
            return BackpressureState.ELEVATED
        
        return BackpressureState.NORMAL
    
    def should_throttle(self) -> bool:
        """Check if system should throttle new requests"""
        with self.state_lock:
            return self.current_state in [BackpressureState.HIGH, BackpressureState.CRITICAL]
    
    def get_recommended_mode(self, workload: HybridWorkload) -> ProcessingMode:
        """Get recommended processing mode based on current state"""
        with self.state_lock:
            if self.current_state == BackpressureState.CRITICAL:
                # Use most efficient mode
                return ProcessingMode.ASYNC_ONLY
            elif self.current_state == BackpressureState.HIGH:
                # Reduce parallelism
                return ProcessingMode.HYBRID_MEMORY
            elif self.current_state == BackpressureState.ELEVATED:
                # Balanced approach
                return ProcessingMode.HYBRID_BALANCED
            else:
                # Normal - can use any mode
                return workload.processing_mode
    
    def update_metrics(self, **kwargs):
        """Update backpressure metrics"""
        for key, value in kwargs.items():
            if key in self.metrics:
                if key == 'response_times':
                    self.metrics[key].append(value)
                else:
                    self.metrics[key] = value
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current backpressure metrics"""
        with self.state_lock:
            return {
                'state': self.current_state.name,
                'metrics': self.metrics.copy(),
                'avg_response_time': sum(self.metrics['response_times']) / len(self.metrics['response_times']) if self.metrics['response_times'] else 0.0
            }

class TelemetryCollector:
    """Collects observability metrics and telemetry"""
    
    def __init__(self):
        self.metrics = defaultdict(lambda: defaultdict(float))
        self.counters = defaultdict(int)
        self.histograms = defaultdict(lambda: deque(maxlen=1000))
        self.metrics_lock = Lock()
        
        # Performance tracking
        self.processing_times = defaultdict(lambda: deque(maxlen=100))
        self.error_rates = defaultdict(lambda: deque(maxlen=100))
        self.throughput_samples = deque(maxlen=100)
        
        logger.info("[TelemetryCollector] 📊 Telemetry collection initialized")
    
    def record_processing_time(self, component: str, operation: str, duration: float):
        """Record processing time for an operation"""
        with self.metrics_lock:
            key = f"{component}.{operation}"
            self.metrics[key]['total_time'] += duration
            self.metrics[key]['count'] += 1
            self.metrics[key]['avg_time'] = self.metrics[key]['total_time'] / self.metrics[key]['count']
            self.processing_times[key].append(duration)
    
    def record_counter(self, metric_name: str, value: int = 1):
        """Record counter metric"""
        with self.metrics_lock:
            self.counters[metric_name] += value
    
    def record_histogram(self, metric_name: str, value: float):
        """Record histogram value"""
        with self.metrics_lock:
            self.histograms[metric_name].append(value)
    
    def record_error(self, component: str, error_type: str):
        """Record error occurrence"""
        with self.metrics_lock:
            error_key = f"{component}.errors.{error_type}"
            self.counters[error_key] += 1
            
            # Update error rate
            rate_key = f"{component}.error_rate"
            self.error_rates[rate_key].append(1.0)
    
    def record_success(self, component: str):
        """Record successful operation"""
        with self.metrics_lock:
            rate_key = f"{component}.error_rate"
            self.error_rates[rate_key].append(0.0)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        with self.metrics_lock:
            return {
                'processing_times': {
                    key: {
                        'avg': self.metrics[key]['avg_time'],
                        'total': self.metrics[key]['total_time'],
                        'count': self.metrics[key]['count'],
                        'p95': self._calculate_percentile(self.processing_times[key], 95),
                        'p99': self._calculate_percentile(self.processing_times[key], 99)
                    } for key in self.metrics
                },
                'counters': dict(self.counters),
                'histograms': {
                    name: {
                        'count': len(values),
                        'avg': sum(values) / len(values) if values else 0.0,
                        'min': min(values) if values else 0.0,
                        'max': max(values) if values else 0.0,
                        'p50': self._calculate_percentile(values, 50),
                        'p95': self._calculate_percentile(values, 95)
                    } for name, values in self.histograms.items()
                },
                'error_rates': {
                    key: sum(values) / len(values) if values else 0.0
                    for key, values in self.error_rates.items()
                }
            }
    
    def _calculate_percentile(self, values: deque, percentile: float) -> float:
        """Calculate percentile of values"""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = int((percentile / 100.0) * len(sorted_values))
        return sorted_values[min(index, len(sorted_values) - 1)]

class HybridConsciousnessWorker(EventSubscriber):
    """Hybrid worker that combines all reactive neural architecture approaches"""
    
    def __init__(self, worker_id: str, event_bus: EventBus, async_pathways: AsyncNeuralPathways,
                 work_stealing_pool: WorkStealingThreadPool, memory_manager: OptimizedMemoryManager,
                 parallel_processor: ParallelConsciousnessProcessor):
        self.worker_id = worker_id
        self.event_bus = event_bus
        self.async_pathways = async_pathways
        self.work_stealing_pool = work_stealing_pool
        self.memory_manager = memory_manager
        self.parallel_processor = parallel_processor
        
        # Worker state
        self.active_workloads: Dict[str, HybridWorkload] = {}
        self.workloads_lock = Lock()
        
        # Subscribe to relevant events
        self.event_bus.subscribe("CONSCIOUSNESS_UPDATE", self)
        self.event_bus.subscribe("USER_INPUT", self)
        self.event_bus.subscribe("INTEGRATION_REQUEST", self)
        
        logger.info(f"[HybridWorker] 🤖 Worker {worker_id} initialized")
    
    async def handle_event(self, event: NeuralEvent) -> bool:
        """Handle events in the hybrid worker"""
        try:
            if event.type == EventType.USER_INPUT:
                return await self._handle_user_input(event)
            elif event.type == EventType.CONSCIOUSNESS_UPDATE:
                return await self._handle_consciousness_update(event)
            elif event.type == EventType.INTEGRATION_REQUEST:
                return await self._handle_integration_request(event)
            else:
                logger.debug(f"[HybridWorker] 🔄 Unhandled event type: {event.type}")
                return True
                
        except Exception as e:
            logger.error(f"[HybridWorker] ❌ Event handling error: {e}")
            return False
    
    async def _handle_user_input(self, event: NeuralEvent) -> bool:
        """Handle user input event"""
        workload = HybridWorkload(
            text=event.data.get('text', ''),
            user=event.data.get('user', ''),
            processing_mode=ProcessingMode.HYBRID_PERFORMANCE,
            priority=event.priority,
            correlation_id=event.correlation_id
        )
        
        result = await self.process_workload(workload)
        
        # Publish result event
        result_event = NeuralEvent(
            type=EventType.USER_RESPONSE,
            priority=event.priority,
            source=self.worker_id,
            data={'result': result, 'original_event_id': event.id},
            correlation_id=event.correlation_id
        )
        await self.event_bus.publish_async(result_event)
        
        return result.success
    
    async def _handle_consciousness_update(self, event: NeuralEvent) -> bool:
        """Handle consciousness update event"""
        # Process consciousness update through appropriate pathway
        operation_id = f"consciousness_{event.id}"
        
        try:
            result = await self.async_pathways.execute_compute_operation(
                operation_id,
                self._update_consciousness_state,
                event.data
            )
            return True
        except Exception as e:
            logger.error(f"[HybridWorker] ❌ Consciousness update error: {e}")
            return False
    
    async def _handle_integration_request(self, event: NeuralEvent) -> bool:
        """Handle integration request event"""
        # Complex integration using multiple pathways
        try:
            # Use parallel processor for consciousness modules
            consciousness_result = await asyncio.get_event_loop().run_in_executor(
                None,
                self.parallel_processor.process_consciousness_parallel,
                event.data.get('text', ''),
                event.data.get('user', '')
            )
            
            # Use async pathways for I/O operations
            io_result = await self.async_pathways.execute_io_operation(
                f"io_{event.id}",
                self._perform_io_operations,
                consciousness_result
            )
            
            return True
            
        except Exception as e:
            logger.error(f"[HybridWorker] ❌ Integration error: {e}")
            return False
    
    def get_subscription_patterns(self) -> List[str]:
        """Return subscription patterns for this worker"""
        return ["USER_INPUT", "CONSCIOUSNESS_UPDATE", "INTEGRATION_REQUEST"]
    
    async def process_workload(self, workload: HybridWorkload) -> ProcessingResult:
        """Process workload using appropriate hybrid approach"""
        start_time = time.time()
        
        with self.workloads_lock:
            self.active_workloads[workload.id] = workload
        
        try:
            # Determine processing approach based on mode
            if workload.processing_mode == ProcessingMode.REACTIVE_ONLY:
                result = await self._process_reactive_only(workload)
            elif workload.processing_mode == ProcessingMode.ASYNC_ONLY:
                result = await self._process_async_only(workload)
            elif workload.processing_mode == ProcessingMode.PARALLEL_ONLY:
                result = await self._process_parallel_only(workload)
            else:
                # Hybrid approaches
                result = await self._process_hybrid(workload)
            
            processing_time = time.time() - start_time
            
            return ProcessingResult(
                workload_id=workload.id,
                success=True,
                result=result,
                processing_time=processing_time,
                mode_used=workload.processing_mode,
                resources_used=self._get_resource_usage()
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"[HybridWorker] ❌ Workload processing error: {e}")
            
            return ProcessingResult(
                workload_id=workload.id,
                success=False,
                result=None,
                processing_time=processing_time,
                mode_used=workload.processing_mode,
                resources_used=self._get_resource_usage(),
                error=str(e)
            )
        finally:
            with self.workloads_lock:
                if workload.id in self.active_workloads:
                    del self.active_workloads[workload.id]
    
    async def _process_reactive_only(self, workload: HybridWorkload) -> Any:
        """Process using reactive/event-driven approach only"""
        # Create processing event
        processing_event = NeuralEvent(
            type=EventType.CONSCIOUSNESS_UPDATE,
            priority=workload.priority,
            source=self.worker_id,
            data={'text': workload.text, 'user': workload.user},
            correlation_id=workload.correlation_id
        )
        
        # Publish and wait for result
        await self.event_bus.publish_async(processing_event)
        
        # Simulate event-driven processing result
        return {'method': 'reactive', 'status': 'completed'}
    
    async def _process_async_only(self, workload: HybridWorkload) -> Any:
        """Process using async pathways only"""
        # Execute consciousness processing asynchronously
        consciousness_result = await self.async_pathways.execute_compute_operation(
            f"consciousness_{workload.id}",
            self._simulate_consciousness_processing,
            workload.text,
            workload.user
        )
        
        # Execute LLM operation asynchronously
        llm_result = await self.async_pathways.execute_llm_operation(
            f"llm_{workload.id}",
            self._simulate_llm_processing,
            consciousness_result
        )
        
        return {'method': 'async', 'consciousness': consciousness_result, 'llm': llm_result}
    
    async def _process_parallel_only(self, workload: HybridWorkload) -> Any:
        """Process using parallel processing only"""
        # Use existing parallel processor
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            self.parallel_processor.process_consciousness_parallel,
            workload.text,
            workload.user
        )
        
        return {'method': 'parallel', 'result': result}
    
    async def _process_hybrid(self, workload: HybridWorkload) -> Any:
        """Process using hybrid approach combining all methods"""
        # Step 1: Use parallel processing for consciousness modules
        consciousness_future = asyncio.get_event_loop().run_in_executor(
            None,
            self.parallel_processor.process_consciousness_parallel,
            workload.text,
            workload.user
        )
        
        # Step 2: Use async pathways for I/O operations concurrently
        io_future = self.async_pathways.execute_io_operation(
            f"hybrid_io_{workload.id}",
            self._simulate_io_operations,
            workload.text
        )
        
        # Step 3: Use event system for coordination
        coordination_event = NeuralEvent(
            type=EventType.CONSCIOUSNESS_UPDATE,
            priority=workload.priority,
            source=self.worker_id,
            data={'workload_id': workload.id, 'stage': 'hybrid_processing'},
            correlation_id=workload.correlation_id
        )
        await self.event_bus.publish_async(coordination_event)
        
        # Wait for all operations to complete
        consciousness_result, io_result = await asyncio.gather(
            consciousness_future,
            io_future,
            return_exceptions=True
        )
        
        # Use work-stealing pool for final integration
        integration_event = self.work_stealing_pool.submit(
            self._integrate_hybrid_results,
            consciousness_result,
            io_result,
            workload
        )
        integration_event.wait(timeout=10.0)
        
        return {
            'method': 'hybrid',
            'consciousness': consciousness_result,
            'io': io_result,
            'integration': 'completed'
        }
    
    def _simulate_consciousness_processing(self, text: str, user: str) -> Dict[str, Any]:
        """Simulate consciousness processing"""
        time.sleep(0.1)  # Simulate processing time
        return {
            'text_analysis': f"Analyzed: {text[:50]}...",
            'user_context': user,
            'consciousness_state': 'active'
        }
    
    def _simulate_llm_processing(self, consciousness_result: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate LLM processing"""
        time.sleep(0.2)  # Simulate LLM call
        return {
            'response': f"Generated response based on: {consciousness_result}",
            'confidence': 0.85
        }
    
    def _simulate_io_operations(self, text: str) -> Dict[str, Any]:
        """Simulate I/O operations"""
        time.sleep(0.05)  # Simulate I/O
        return {
            'external_data': f"External context for: {text[:30]}...",
            'cache_updated': True
        }
    
    def _integrate_hybrid_results(self, consciousness_result: Any, io_result: Any, workload: HybridWorkload) -> Dict[str, Any]:
        """Integrate results from hybrid processing"""
        return {
            'final_result': 'Integration completed',
            'consciousness': consciousness_result,
            'io': io_result,
            'workload_id': workload.id
        }
    
    def _update_consciousness_state(self, data: Dict[str, Any]) -> bool:
        """Update consciousness state"""
        # Use memory manager for state updates
        state_snapshot = self.memory_manager.create_cow_object(
            f"consciousness_state_{int(time.time())}",
            data
        )
        return True
    
    def _perform_io_operations(self, consciousness_result: Dict[str, Any]) -> Dict[str, Any]:
        """Perform I/O operations"""
        time.sleep(0.1)  # Simulate I/O
        return {'io_completed': True, 'data': consciousness_result}
    
    def _get_resource_usage(self) -> Dict[str, Any]:
        """Get current resource usage"""
        if psutil:
            try:
                process = psutil.Process()
                return {
                    'cpu_percent': process.cpu_percent(),
                    'memory_mb': process.memory_info().rss / (1024 * 1024),
                    'threads': process.num_threads()
                }
            except:
                pass
        
        return {
            'cpu_percent': 0.0,
            'memory_mb': 0.0,
            'threads': threading.active_count()
        }

class ReactiveIntegrationLayer:
    """Main integration layer coordinating all reactive neural architecture components"""
    
    def __init__(self, num_workers: int = 4):
        self.num_workers = num_workers
        
        # Initialize reactive components
        self.event_bus = EventBus()
        self.async_pathways = AsyncNeuralPathways()
        self.work_stealing_pool = WorkStealingThreadPool()
        self.memory_manager = OptimizedMemoryManager()
        self.parallel_processor = ParallelConsciousnessProcessor()
        
        # Initialize integration components
        self.backpressure_manager = BackpressureManager()
        self.telemetry_collector = TelemetryCollector()
        
        # Create hybrid workers
        self.workers: List[HybridConsciousnessWorker] = []
        self.worker_round_robin = 0
        self.workers_lock = Lock()
        
        # System state
        self.initialized = False
        self.shutdown_event = Event()
        
        logger.info(f"[ReactiveIntegrationLayer] 🚀 Integration layer initializing with {num_workers} workers")
    
    async def initialize(self):
        """Initialize the complete reactive neural architecture"""
        if self.initialized:
            return
        
        # Initialize async components
        await self.event_bus.initialize_async()
        
        # Setup parallel processor
        self.parallel_processor.setup_default_modules()
        
        # Create hybrid workers
        for i in range(self.num_workers):
            worker = HybridConsciousnessWorker(
                worker_id=f"hybrid_worker_{i}",
                event_bus=self.event_bus,
                async_pathways=self.async_pathways,
                work_stealing_pool=self.work_stealing_pool,
                memory_manager=self.memory_manager,
                parallel_processor=self.parallel_processor
            )
            self.workers.append(worker)
        
        self.initialized = True
        logger.info("[ReactiveIntegrationLayer] ✅ Reactive neural architecture fully initialized")
    
    async def process_user_input(self, text: str, user: str, processing_mode: ProcessingMode = ProcessingMode.HYBRID_BALANCED) -> ProcessingResult:
        """Process user input through the reactive neural architecture"""
        if not self.initialized:
            await self.initialize()
        
        # Check backpressure
        if self.backpressure_manager.should_throttle():
            logger.warning("[ReactiveIntegrationLayer] ⚠️ System under high load, throttling request")
            raise Exception("System overloaded, please try again later")
        
        # Get recommended processing mode
        workload = HybridWorkload(
            text=text,
            user=user,
            processing_mode=processing_mode
        )
        
        recommended_mode = self.backpressure_manager.get_recommended_mode(workload)
        workload.processing_mode = recommended_mode
        
        # Select worker using round-robin
        with self.workers_lock:
            worker = self.workers[self.worker_round_robin]
            self.worker_round_robin = (self.worker_round_robin + 1) % len(self.workers)
        
        # Record telemetry
        start_time = time.time()
        
        try:
            # Process workload
            result = await worker.process_workload(workload)
            
            # Update telemetry
            processing_time = time.time() - start_time
            self.telemetry_collector.record_processing_time("integration", "user_input", processing_time)
            self.telemetry_collector.record_success("integration")
            
            # Update backpressure metrics
            self.backpressure_manager.update_metrics(response_times=processing_time)
            
            logger.info(f"[ReactiveIntegrationLayer] ✅ Processed input in {processing_time:.3f}s using {recommended_mode.name}")
            return result
            
        except Exception as e:
            # Record error
            self.telemetry_collector.record_error("integration", "processing_error")
            logger.error(f"[ReactiveIntegrationLayer] ❌ Processing failed: {e}")
            raise
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health metrics"""
        loop = _ensure_loop()
        async_pathways_stats = (
            loop.run_until_complete(self.async_pathways.get_stats())
            if self.initialized else {}
        )

        return {
            'backpressure': self.backpressure_manager.get_metrics(),
            'telemetry': self.telemetry_collector.get_metrics_summary(),
            'event_bus': self.event_bus.get_stats(),
            'async_pathways': async_pathways_stats,
            'work_stealing_pool': self.work_stealing_pool.get_stats(),
            'memory_manager': self.memory_manager.get_memory_stats(),
            'parallel_processor': self.parallel_processor.get_performance_report() if hasattr(self.parallel_processor, 'get_performance_report') else {},
            'workers': {
                'count': len(self.workers),
                'active_workloads': sum(len(worker.active_workloads) for worker in self.workers)
            }
        }
    
    async def shutdown(self):
        """Shutdown the reactive neural architecture gracefully"""
        logger.info("[ReactiveIntegrationLayer] 🛑 Initiating graceful shutdown")
        
        self.shutdown_event.set()
        
        # Shutdown components
        await self.event_bus.shutdown()
        await self.async_pathways.cancel_all_operations()
        self.work_stealing_pool.shutdown(wait=True)
        self.memory_manager.cleanup()
        
        # Stop backpressure monitoring
        self.backpressure_manager.monitoring_active = False
        
        logger.info("[ReactiveIntegrationLayer] ✅ Reactive neural architecture shutdown complete")
    
    @asynccontextmanager
    async def context_manager(self):
        """Context manager for automatic initialization and cleanup"""
        try:
            await self.initialize()
            yield self
        finally:
            await self.shutdown()

# Global instance
reactive_integration_layer = ReactiveIntegrationLayer()

def get_reactive_integration_layer() -> ReactiveIntegrationLayer:
    """Get the global reactive integration layer"""
    return reactive_integration_layer

async def initialize_reactive_integration():
    """Initialize the reactive integration layer"""
    await reactive_integration_layer.initialize()
    return reactive_integration_layer