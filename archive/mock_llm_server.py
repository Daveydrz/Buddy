#!/usr/bin/env python3
"""
Mock LLM Server for Testing Integration
Created: 2025-01-17
Purpose: Test LLM integration when KoboldCPP isn't available
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time
import sys

class MockLLMHandler(BaseHTTPRequestHandler):
    """Mock LLM server handler"""
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/v1/models':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                "object": "list",
                "data": [
                    {
                        "id": "llama3-mock",
                        "object": "model",
                        "owned_by": "mock-server"
                    }
                ]
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/v1/chat/completions':
            # Read the request
            content_length = int(self.headers.get('Content-Length', 0))
            request_data = self.rfile.read(content_length).decode('utf-8')
            
            try:
                request_json = json.loads(request_data)
                stream = request_json.get('stream', False)
                
                if stream:
                    # Streaming response
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/event-stream')
                    self.send_header('Cache-Control', 'no-cache')
                    self.send_header('Connection', 'keep-alive')
                    self.end_headers()
                    
                    # Send streaming chunks
                    response_text = "This is a mock LLM response for testing integration. All components are working correctly with consciousness tokenization and prompt integration."
                    words = response_text.split()
                    
                    for i, word in enumerate(words):
                        chunk = {
                            "choices": [{
                                "delta": {"content": word + " "},
                                "finish_reason": None if i < len(words) - 1 else "stop"
                            }]
                        }
                        
                        data = f"data: {json.dumps(chunk)}\n\n"
                        self.wfile.write(data.encode())
                        self.wfile.flush()
                        time.sleep(0.1)  # Simulate streaming delay
                    
                    # Send final chunk
                    self.wfile.write(b"data: [DONE]\n\n")
                    self.wfile.flush()
                else:
                    # Non-streaming response
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    
                    response = {
                        "choices": [{
                            "message": {
                                "content": "This is a mock LLM response for testing integration. All components are working correctly with consciousness tokenization and prompt integration."
                            },
                            "finish_reason": "stop"
                        }],
                        "usage": {
                            "prompt_tokens": 50,
                            "completion_tokens": 25,
                            "total_tokens": 75
                        }
                    }
                    
                    self.wfile.write(json.dumps(response).encode())
            
            except Exception as e:
                self.send_error(500, f"Error processing request: {e}")
        else:
            self.send_error(404)
    
    def log_message(self, format, *args):
        """Override logging to be quieter"""
        pass

def start_mock_server(port=5001):
    """Start mock LLM server"""
    server = HTTPServer(('localhost', port), MockLLMHandler)
    
    def run_server():
        print(f"🤖 Mock LLM Server started on http://localhost:{port}")
        print("📡 Ready to receive requests...")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Mock LLM Server stopped")
            server.server_close()
    
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    
    return server

def test_mock_server():
    """Test the mock server"""
    import requests
    
    print("🧪 Testing Mock LLM Server...")
    
    try:
        # Test models endpoint
        response = requests.get("http://localhost:5001/v1/models", timeout=5)
        if response.status_code == 200:
            print("✅ Models endpoint working")
        else:
            print(f"❌ Models endpoint failed: {response.status_code}")
        
        # Test chat completion
        payload = {
            "model": "llama3-mock",
            "messages": [{"role": "user", "content": "Hello, test message"}],
            "max_tokens": 50,
            "temperature": 0.7,
            "stream": False
        }
        
        response = requests.post("http://localhost:5001/v1/chat/completions", json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            print(f"✅ Chat completion working: {content[:50]}...")
        else:
            print(f"❌ Chat completion failed: {response.status_code}")
        
        # Test streaming
        payload['stream'] = True
        response = requests.post("http://localhost:5001/v1/chat/completions", json=payload, stream=True, timeout=10)
        if response.status_code == 200:
            chunks = []
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    if line_text.startswith('data: ') and not line_text.endswith('[DONE]'):
                        try:
                            chunk_data = json.loads(line_text[6:])
                            if 'choices' in chunk_data:
                                content = chunk_data['choices'][0]['delta'].get('content', '')
                                if content:
                                    chunks.append(content)
                        except:
                            pass
            
            if chunks:
                print(f"✅ Streaming working: {len(chunks)} chunks received")
            else:
                print("❌ Streaming failed: No chunks received")
        else:
            print(f"❌ Streaming failed: {response.status_code}")
            
        print("🎉 Mock LLM Server test complete!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Just run the test
        test_mock_server()
    else:
        # Start the server
        server = start_mock_server()
        
        # Wait a bit then test
        time.sleep(1)
        test_mock_server()
        
        print("\n🚀 Mock LLM Server is running!")
        print("💡 Use this for testing when KoboldCPP isn't available")
        print("🔗 API endpoint: http://localhost:5001/v1/chat/completions")
        print("🛑 Press Ctrl+C to stop")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Stopping mock server...")
            server.server_close()