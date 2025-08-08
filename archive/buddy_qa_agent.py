#!/usr/bin/env python3
"""
Buddy Q&A Agent - Advanced Testing and Monitoring System
Created: 2025-01-17
Purpose: Launch main.py as subprocess, capture all logs, and produce comprehensive analysis
"""

import subprocess
import json
import time
import threading
import signal
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import re
import queue

class BuddyQAAgent:
    """
    Advanced Q&A agent that monitors Buddy's performance and detects issues
    """
    
    def __init__(self, session_timeout: int = 300):
        self.session_timeout = session_timeout
        self.session_start = None
        self.process = None
        self.stdout_queue = queue.Queue()
        self.stderr_queue = queue.Queue()
        self.session_logs = []
        self.detected_issues = []
        self.optimization_suggestions = []
        self.performance_metrics = {}
        
        # Log pattern matchers
        self.log_patterns = {
            'whisper_transcription_end': r'\[DETAILED_LOG\] 🎤 WHISPER_TRANSCRIPTION_END: \'([^\']*)\' \| user=\'([^\']*)\' \| timestamp=([^\s]*)',
            'llm_request_start': r'\[DETAILED_LOG\] 🤖 LLM_REQUEST_START: \'([^\']*)\' \| user=\'([^\']*)\' \| timestamp=([^\s]*)',
            'llm_first_token': r'\[DETAILED_LOG\] 🤖 LLM_FIRST_TOKEN: \'([^\']*)\' \| timestamp=([^\s]*)',
            'llm_last_token': r'\[DETAILED_LOG\] 🤖 LLM_LAST_TOKEN: chunk_(\d+) \| timestamp=([^\s]*)',
            'consciousness_prompt_injection': r'\[DETAILED_LOG\] 🧠 CONSCIOUSNESS_PROMPT_INJECTION: tier=([^\s]*) \| tokens=(\d+) \| timestamp=([^\s]*)',
            'belief_memory_update': r'\[DETAILED_LOG\] 💭 BELIEF_MEMORY_UPDATE: modules=(\d+) \| timestamp=([^\s]*)',
            'kokoro_playback_start': r'\[DETAILED_LOG\] 🎵 KOKORO_PLAYBACK_START: ([^\|]*) \| text=\'([^\']*)\' \| timestamp=([^\s]*)',
            'kokoro_playback_end': r'\[DETAILED_LOG\] 🎵 KOKORO_PLAYBACK_END: ([^\|]*) \| ([^\|]*) \| timestamp=([^\s]*)',
            'error': r'\[.*\] ❌ ([^\n]*)',
            'warning': r'\[.*\] ⚠️ ([^\n]*)',
            'infinite_loop': r'You are Buddy, a Class 5\+ synthetic consciousness',
            'stuck_state': r'currently processing another request',
            'method_error': r'missing \d+ required positional argument'
        }
        
    def start_session(self):
        """Start a Buddy monitoring session"""
        print("[BuddyQA] 🚀 Starting Buddy Q&A monitoring session...")
        self.session_start = datetime.now()
        
        try:
            # Start main.py as subprocess
            self.process = subprocess.Popen(
                [sys.executable, 'main.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=Path(__file__).parent
            )
            
            # Start log capture threads
            self._start_log_capture_threads()
            
            print(f"[BuddyQA] ✅ Buddy process started (PID: {self.process.pid})")
            print(f"[BuddyQA] ⏰ Session timeout: {self.session_timeout}s")
            print(f"[BuddyQA] 📊 Monitoring all detailed logs...")
            
            return True
            
        except Exception as e:
            print(f"[BuddyQA] ❌ Failed to start Buddy process: {e}")
            return False
    
    def _start_log_capture_threads(self):
        """Start threads to capture stdout and stderr"""
        def capture_stdout():
            try:
                for line in iter(self.process.stdout.readline, ''):
                    if line:
                        self.stdout_queue.put((datetime.now(), line.strip()))
                        self._process_log_line(line.strip(), 'stdout')
            except Exception as e:
                print(f"[BuddyQA] ⚠️ Stdout capture error: {e}")
        
        def capture_stderr():
            try:
                for line in iter(self.process.stderr.readline, ''):
                    if line:
                        self.stderr_queue.put((datetime.now(), line.strip()))
                        self._process_log_line(line.strip(), 'stderr')
            except Exception as e:
                print(f"[BuddyQA] ⚠️ Stderr capture error: {e}")
        
        threading.Thread(target=capture_stdout, daemon=True).start()
        threading.Thread(target=capture_stderr, daemon=True).start()
    
    def _process_log_line(self, line: str, source: str):
        """Process a single log line and extract meaningful data"""
        timestamp = datetime.now()
        
        # Store raw log
        log_entry = {
            'timestamp': timestamp.isoformat(),
            'source': source,
            'content': line
        }
        self.session_logs.append(log_entry)
        
        # Pattern matching for detailed analysis
        for pattern_name, pattern in self.log_patterns.items():
            match = re.search(pattern, line)
            if match:
                self._handle_pattern_match(pattern_name, match, timestamp, line)
        
        # Real-time issue detection
        self._detect_issues_realtime(line, timestamp)
    
    def _handle_pattern_match(self, pattern_name: str, match, timestamp: datetime, line: str):
        """Handle specific pattern matches"""
        if pattern_name == 'llm_request_start':
            self.performance_metrics['last_llm_request'] = {
                'timestamp': timestamp.isoformat(),
                'text': match.group(1)[:50],
                'user': match.group(2)
            }
        
        elif pattern_name == 'llm_first_token':
            if 'last_llm_request' in self.performance_metrics:
                start_time = datetime.fromisoformat(self.performance_metrics['last_llm_request']['timestamp'])
                latency = (timestamp - start_time).total_seconds()
                self.performance_metrics['first_token_latency'] = latency
                
                if latency > 5.0:
                    self.detected_issues.append({
                        'type': 'performance',
                        'severity': 'high',
                        'message': f'High first token latency: {latency:.2f}s',
                        'timestamp': timestamp.isoformat()
                    })
        
        elif pattern_name == 'consciousness_prompt_injection':
            token_count = int(match.group(2))
            if token_count > 100:
                self.detected_issues.append({
                    'type': 'optimization',
                    'severity': 'medium',
                    'message': f'High consciousness token count: {token_count}',
                    'timestamp': timestamp.isoformat()
                })
        
        elif pattern_name == 'kokoro_playback_start':
            self.performance_metrics['last_kokoro_start'] = timestamp.isoformat()
        
        elif pattern_name == 'kokoro_playback_end':
            if 'last_kokoro_start' in self.performance_metrics:
                start_time = datetime.fromisoformat(self.performance_metrics['last_kokoro_start'])
                playback_time = (timestamp - start_time).total_seconds()
                self.performance_metrics['last_kokoro_duration'] = playback_time
    
    def _detect_issues_realtime(self, line: str, timestamp: datetime):
        """Detect issues in real-time"""
        # Infinite loop detection
        if re.search(self.log_patterns['infinite_loop'], line):
            self.detected_issues.append({
                'type': 'critical',
                'severity': 'critical',
                'message': 'Infinite consciousness prompt loop detected',
                'timestamp': timestamp.isoformat(),
                'line': line
            })
        
        # Stuck state detection
        if re.search(self.log_patterns['stuck_state'], line):
            self.detected_issues.append({
                'type': 'blocking',
                'severity': 'high',
                'message': 'LLM stuck in processing state',
                'timestamp': timestamp.isoformat()
            })
        
        # Method errors
        if re.search(self.log_patterns['method_error'], line):
            self.detected_issues.append({
                'type': 'code_error',
                'severity': 'high',
                'message': 'Method call error detected',
                'timestamp': timestamp.isoformat(),
                'line': line
            })
    
    def run_interactive_test(self, duration_minutes: int = 5):
        """Run an interactive test session"""
        print(f"[BuddyQA] 🎯 Running {duration_minutes}-minute interactive test...")
        
        if not self.start_session():
            return False
        
        try:
            # Wait for Buddy to initialize
            print("[BuddyQA] ⏳ Waiting for Buddy initialization...")
            time.sleep(10)
            
            # Monitor for specified duration
            end_time = datetime.now() + timedelta(minutes=duration_minutes)
            
            while datetime.now() < end_time and self.process.poll() is None:
                time.sleep(1)
                
                # Print periodic status
                if datetime.now().second % 30 == 0:
                    issues_count = len(self.detected_issues)
                    logs_count = len(self.session_logs)
                    print(f"[BuddyQA] 📊 Status: {logs_count} logs, {issues_count} issues detected")
            
            print("[BuddyQA] ⏰ Test duration completed")
            return True
            
        except KeyboardInterrupt:
            print("\n[BuddyQA] ⚡ Test interrupted by user")
            return True
        
        finally:
            self.stop_session()
    
    def stop_session(self):
        """Stop the monitoring session"""
        print("[BuddyQA] 🛑 Stopping Buddy monitoring session...")
        
        if self.process and self.process.poll() is None:
            try:
                # Send SIGTERM first
                self.process.terminate()
                
                # Wait up to 5 seconds for graceful shutdown
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if needed
                    self.process.kill()
                    self.process.wait()
                
                print(f"[BuddyQA] ✅ Buddy process stopped")
            except Exception as e:
                print(f"[BuddyQA] ⚠️ Error stopping process: {e}")
    
    def generate_analysis_report(self):
        """Generate comprehensive analysis report"""
        print("[BuddyQA] 📊 Generating analysis report...")
        
        # Analyze performance
        self._analyze_performance()
        
        # Generate optimization suggestions
        self._generate_optimization_suggestions()
        
        # Create session logs JSON
        session_data = {
            'session_info': {
                'start_time': self.session_start.isoformat() if self.session_start else None,
                'end_time': datetime.now().isoformat(),
                'duration_seconds': (datetime.now() - self.session_start).total_seconds() if self.session_start else 0,
                'total_logs': len(self.session_logs),
                'total_issues': len(self.detected_issues)
            },
            'performance_metrics': self.performance_metrics,
            'detected_issues': self.detected_issues,
            'optimization_suggestions': self.optimization_suggestions,
            'session_logs': self.session_logs[-500:]  # Keep last 500 logs
        }
        
        # Save session logs
        with open('session_logs.json', 'w') as f:
            json.dump(session_data, f, indent=2)
        
        # Generate text report
        self._generate_text_report(session_data)
        
        print("[BuddyQA] ✅ Analysis complete: session_logs.json and report.txt generated")
    
    def _analyze_performance(self):
        """Analyze performance metrics"""
        # Count log types
        log_counts = {}
        for log_entry in self.session_logs:
            for pattern_name, pattern in self.log_patterns.items():
                if re.search(pattern, log_entry['content']):
                    log_counts[pattern_name] = log_counts.get(pattern_name, 0) + 1
        
        self.performance_metrics['log_type_counts'] = log_counts
        
        # Calculate average latencies if available
        if 'first_token_latency' in self.performance_metrics:
            self.performance_metrics['performance_rating'] = 'good' if self.performance_metrics['first_token_latency'] < 3.0 else 'needs_improvement'
    
    def _generate_optimization_suggestions(self):
        """Generate optimization suggestions based on detected issues"""
        issue_types = [issue['type'] for issue in self.detected_issues]
        
        if 'critical' in issue_types:
            self.optimization_suggestions.append({
                'priority': 'critical',
                'suggestion': 'Fix infinite consciousness prompt loops by adding detection in LLM handler',
                'impact': 'Prevents system from becoming unresponsive'
            })
        
        if 'performance' in issue_types:
            self.optimization_suggestions.append({
                'priority': 'high',
                'suggestion': 'Optimize LLM latency by reducing consciousness token count or using faster model',
                'impact': 'Improves response time from 5s+ to <3s'
            })
        
        if 'blocking' in issue_types:
            self.optimization_suggestions.append({
                'priority': 'high',
                'suggestion': 'Implement auto-reset for stuck LLM states after 60 seconds',
                'impact': 'Prevents permanent blocking of user requests'
            })
        
        if 'code_error' in issue_types:
            self.optimization_suggestions.append({
                'priority': 'medium',
                'suggestion': 'Fix method call errors by ensuring proper parameter passing',
                'impact': 'Eliminates runtime crashes'
            })
        
        # General optimizations
        if self.performance_metrics.get('log_type_counts', {}).get('consciousness_prompt_injection', 0) > 10:
            self.optimization_suggestions.append({
                'priority': 'medium',
                'suggestion': 'Optimize consciousness token usage to reduce prompt size',
                'impact': 'Reduces token costs and improves processing speed'
            })
    
    def _generate_text_report(self, session_data: Dict[str, Any]):
        """Generate human-readable text report"""
        report_lines = [
            "="*60,
            "BUDDY Q&A AGENT - SESSION ANALYSIS REPORT",
            "="*60,
            "",
            f"Session Duration: {session_data['session_info']['duration_seconds']:.1f} seconds",
            f"Total Logs Captured: {session_data['session_info']['total_logs']}",
            f"Issues Detected: {session_data['session_info']['total_issues']}",
            "",
            "PERFORMANCE METRICS:",
            "-"*30
        ]
        
        for metric, value in session_data['performance_metrics'].items():
            if metric != 'log_type_counts':
                report_lines.append(f"  {metric}: {value}")
        
        if session_data['detected_issues']:
            report_lines.extend([
                "",
                "DETECTED ISSUES:",
                "-"*30
            ])
            
            for issue in session_data['detected_issues']:
                report_lines.append(f"  [{issue['severity'].upper()}] {issue['message']}")
        
        if session_data['optimization_suggestions']:
            report_lines.extend([
                "",
                "OPTIMIZATION SUGGESTIONS:",
                "-"*30
            ])
            
            for suggestion in session_data['optimization_suggestions']:
                report_lines.append(f"  [{suggestion['priority'].upper()}] {suggestion['suggestion']}")
                report_lines.append(f"    Impact: {suggestion['impact']}")
                report_lines.append("")
        
        report_lines.extend([
            "",
            "LOG TYPE BREAKDOWN:",
            "-"*30
        ])
        
        log_counts = session_data['performance_metrics'].get('log_type_counts', {})
        for log_type, count in log_counts.items():
            report_lines.append(f"  {log_type}: {count}")
        
        report_lines.extend([
            "",
            "="*60,
            f"Report generated: {datetime.now().isoformat()}",
            "="*60
        ])
        
        with open('report.txt', 'w') as f:
            f.write('\n'.join(report_lines))

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Buddy Q&A Agent - Advanced Testing and Monitoring')
    parser.add_argument('--duration', type=int, default=5, help='Test duration in minutes (default: 5)')
    parser.add_argument('--timeout', type=int, default=300, help='Session timeout in seconds (default: 300)')
    
    args = parser.parse_args()
    
    print("🤖 Buddy Q&A Agent - Advanced Testing and Monitoring System")
    print("="*60)
    
    agent = BuddyQAAgent(session_timeout=args.timeout)
    
    try:
        # Run interactive test
        success = agent.run_interactive_test(duration_minutes=args.duration)
        
        if success:
            print("\n[BuddyQA] 📊 Generating comprehensive analysis...")
            agent.generate_analysis_report()
            
            print(f"""
✅ SESSION COMPLETE!
   
📄 Files Generated:
   - session_logs.json (detailed log data)
   - report.txt (human-readable analysis)
   
🔍 Summary:
   - Logs captured: {len(agent.session_logs)}
   - Issues detected: {len(agent.detected_issues)}
   - Suggestions: {len(agent.optimization_suggestions)}
   
💡 Next Steps:
   1. Review report.txt for optimization suggestions
   2. Check session_logs.json for detailed log analysis
   3. Address critical and high-priority issues first
""")
        else:
            print("[BuddyQA] ❌ Session failed to start properly")
            return 1
    
    except Exception as e:
        print(f"[BuddyQA] ❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())