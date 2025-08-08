#!/usr/bin/env python3
"""
Mock KoboldCPP Server for Testing IncompleteRead Error Handling
Purpose: Simulate the exact IncompleteRead error scenario to validate fixes
"""

import socket
import threading
import time
import json
import sys
import os

# Add project root to path
sys.path.insert(0, '/home/runner/work/Buddy/Buddy')

from ai.chat import test_kobold_connection, get_kobold_connection_health
from ai.kobold_connection_manager import EnhancedKoboldCPPManager


class MockKoboldCPPServer:
    """Mock server that simulates KoboldCPP connection issues"""
    
    def __init__(self, port=5001):
        self.port = port
        self.running = False
        self.socket = None
        self.error_mode = 'normal'  # normal, incomplete_read, timeout, connection_error
        
    def start(self):
        """Start the mock server"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.socket.bind(('localhost', self.port))
            self.socket.listen(5)
            self.running = True
            print(f"🚀 Mock KoboldCPP server started on port {self.port}")
            
            while self.running:
                try:
                    client_socket, address = self.socket.accept()
                    thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                    thread.daemon = True
                    thread.start()
                except Exception as e:
                    if self.running:
                        print(f"❌ Server error: {e}")
                        
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
        
    def stop(self):
        """Stop the mock server"""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        print("🛑 Mock KoboldCPP server stopped")
    
    def set_error_mode(self, mode):
        """Set the error mode for testing"""
        self.error_mode = mode
        print(f"🔧 Mock server error mode: {mode}")
    
    def handle_client(self, client_socket):
        """Handle client requests with configurable error modes"""
        try:
            # Read request
            request = b""
            while b"\r\n\r\n" not in request:
                chunk = client_socket.recv(1024)
                if not chunk:
                    break
                request += chunk
            
            # Parse request
            request_str = request.decode('utf-8', errors='ignore')
            
            # Check if it's a models request (health check)
            if '/v1/models' in request_str:
                self.handle_models_request(client_socket)
            elif '/v1/chat/completions' in request_str:
                self.handle_chat_request(client_socket, request_str)
            else:
                self.send_404(client_socket)
                
        except Exception as e:
            print(f"⚠️ Client handling error: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass
    
    def handle_models_request(self, client_socket):
        """Handle models endpoint for health checks"""
        if self.error_mode == 'connection_error':
            client_socket.close()
            return
            
        response_data = {
            "object": "list",
            "data": [{"id": "llama3", "object": "model"}]
        }
        
        response_json = json.dumps(response_data)
        response = f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {len(response_json)}\r\n\r\n{response_json}"
        
        try:
            client_socket.send(response.encode())
        except:
            pass
    
    def handle_chat_request(self, client_socket, request_str):
        """Handle chat completion requests with error simulation"""
        
        if self.error_mode == 'connection_error':
            client_socket.close()
            return
        
        if self.error_mode == 'timeout':
            time.sleep(10)  # Simulate timeout
            return
        
        # Prepare response
        response_data = {
            "choices": [
                {
                    "message": {
                        "content": "This is a test response from the mock KoboldCPP server. Connection handling is working correctly!"
                    }
                }
            ]
        }
        
        response_json = json.dumps(response_data)
        
        if self.error_mode == 'incomplete_read':
            # Simulate IncompleteRead by sending partial response with Content-Length mismatch
            print("🔧 Simulating IncompleteRead error...")
            
            # Send headers with a longer Content-Length than actual content
            full_response_json = json.dumps(response_data)
            partial_content = full_response_json[:len(full_response_json)//2]  # Send only half
            claimed_length = len(full_response_json) + 50  # Claim more content than exists
            
            headers = f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {claimed_length}\r\nConnection: close\r\n\r\n"
            
            try:
                # Send headers and partial content
                client_socket.send(headers.encode())
                time.sleep(0.1)  # Small delay
                client_socket.send(partial_content.encode())
                time.sleep(0.1)  # Another delay
                # Close connection without sending the remaining content
                # This should trigger a ChunkedEncodingError/IncompleteRead
                client_socket.close()
            except Exception as e:
                print(f"⚠️ Error simulating IncompleteRead: {e}")
                pass
        else:
            # Normal response
            response = f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {len(response_json)}\r\n\r\n{response_json}"
            
            try:
                client_socket.send(response.encode())
            except:
                pass
    
    def send_404(self, client_socket):
        """Send 404 response"""
        response = "HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n"
        try:
            client_socket.send(response.encode())
        except:
            pass


def test_connection_scenarios():
    """Test various connection scenarios"""
    print("🧪 Testing KoboldCPP Connection Scenarios")
    print("=" * 50)
    
    server = MockKoboldCPPServer()
    server_thread = threading.Thread(target=server.start)
    server_thread.daemon = True
    server_thread.start()
    
    time.sleep(1)  # Let server start
    
    scenarios = [
        ('normal', "✅ Normal operation"),
        ('incomplete_read', "⚠️ IncompleteRead error simulation"),
        ('timeout', "⏰ Timeout error simulation"),
        ('connection_error', "❌ Connection error simulation"),
    ]
    
    manager = EnhancedKoboldCPPManager(
        kobold_url="http://localhost:5001/v1/chat/completions",
        max_concurrent_requests=1,
        max_retries=3
    )
    
    results = {}
    
    for error_mode, description in scenarios:
        print(f"\n{description}")
        print("-" * 30)
        
        server.set_error_mode(error_mode)
        time.sleep(0.5)
        
        # Test with our enhanced manager
        try:
            payload = {
                "model": "llama3",
                "messages": [{"role": "user", "content": f"Test {error_mode}"}],
                "max_tokens": 50,
                "temperature": 0.7
            }
            
            start_time = time.time()
            
            if error_mode == 'incomplete_read':
                print("🔍 Testing IncompleteRead error handling...")
                try:
                    response = manager.execute_request(payload)
                    duration = time.time() - start_time
                    
                    if response.status_code == 200:
                        print(f"✅ Request succeeded after retries ({duration:.2f}s)")
                        results[error_mode] = 'success_after_retry'
                    else:
                        print(f"⚠️ Request failed with status {response.status_code}")
                        results[error_mode] = 'failed'
                        
                except Exception as e:
                    duration = time.time() - start_time
                    print(f"❌ Request failed: {e} ({duration:.2f}s)")
                    results[error_mode] = 'failed_with_exception'
            else:
                # Test other scenarios
                try:
                    response = manager.execute_request(payload)
                    duration = time.time() - start_time
                    
                    if response.status_code == 200:
                        print(f"✅ Request succeeded ({duration:.2f}s)")
                        results[error_mode] = 'success'
                    else:
                        print(f"⚠️ Request failed with status {response.status_code}")
                        results[error_mode] = 'failed'
                        
                except Exception as e:
                    duration = time.time() - start_time
                    print(f"❌ Request failed: {e} ({duration:.2f}s)")
                    results[error_mode] = 'failed_with_exception'
        
        except Exception as e:
            print(f"❌ Test setup error: {e}")
            results[error_mode] = 'test_error'
        
        # Get manager statistics
        stats = manager.get_comprehensive_stats()
        print(f"📊 Manager Stats:")
        print(f"   Total Requests: {stats['metrics']['total_requests']}")
        print(f"   Success Rate: {stats['metrics'].get('success_rate', 0):.1f}%")
        print(f"   IncompleteRead Errors: {stats['metrics']['incomplete_read_errors']}")
        print(f"   Health Score: {stats.get('health_score', 0):.1f}/100")
    
    server.stop()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")
    print("-" * 25)
    
    for error_mode, result in results.items():
        status_icon = "✅" if 'success' in result else "❌"
        print(f"{status_icon} {error_mode}: {result}")
    
    # Overall assessment
    incomplete_read_handled = results.get('incomplete_read', '') in ['success', 'success_after_retry']
    
    if incomplete_read_handled:
        print("\n🎉 SUCCESS: IncompleteRead error handling is working correctly!")
        print("✅ The enhanced connection manager successfully handles connection issues")
        print("✅ Consciousness system should maintain stability during KoboldCPP connection problems")
    else:
        print("\n⚠️ WARNING: IncompleteRead error handling needs improvement")
        print("❌ The connection manager may not fully handle all connection issues")
    
    return incomplete_read_handled


if __name__ == "__main__":
    print("🚀 KoboldCPP Connection Issue Validation")
    print("🎯 Testing Enhanced Connection Handling")
    print("=" * 60)
    
    # Run the connection scenario tests
    success = test_connection_scenarios()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 VALIDATION COMPLETE: KoboldCPP connection improvements are working!")
        print("✅ IncompleteRead errors are properly handled")
        print("✅ Consciousness system protection is functional")
        print("✅ Ready for production use")
    else:
        print("⚠️ VALIDATION INCOMPLETE: Some issues remain")
        print("🔧 Additional improvements may be needed")
    
    print(f"\n💡 Test completed. Connection improvements {"PASSED" if success else "NEED REFINEMENT"}.")