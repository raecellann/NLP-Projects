from __future__ import annotations
import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from typing import Any, Dict, List, Union
from backend import TypingTest

class TypingTestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.typing_test = TypingTest()
        super().__init__(*args, **kwargs)
    
    def do_GET(self) -> None:
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        if path.startswith('/api/'):
            self.handle_api_request(path)
            return
        
        if path == '/' or path == '/index.html':
            self.serve_file('index.html', 'text/html')
        elif path == '/style.css':
            self.serve_file('style.css', 'text/css')
        else:
            self.send_error(404, "File not found")
    
    def handle_api_request(self, path: str) -> None:
        if path == '/api/new_test':
            self.handle_new_test()
        elif path == '/api/more_text':
            self.handle_more_text()
        else:
            self.send_error(404, "API endpoint not found")
    
    def handle_new_test(self) -> None:
        try:
            text: str = self.typing_test.get_random_text(use_ngrams=True, length=30)
            if not text:
                text = self.typing_test.get_random_text(use_ngrams=False, length=30)
            
            words: List[str] = text.split()
            
            response_data: Dict[str, Union[str, List[str]]] = {
                'text': text,
                'words': words
            }
            
            self.send_json_response(response_data)
        except Exception as e:
            self.send_error(500, f"Error creating new test: {str(e)}")
    
    def handle_more_text(self) -> None:
        try:
            text: str = self.typing_test.get_random_text(use_ngrams=True, length=30)
            if not text:
                text = self.typing_test.get_random_text(use_ngrams=False, length=30)
            
            words: List[str] = text.split()
            
            response_data: Dict[str, Union[str, List[str]]] = {
                'text': text,
                'words': words
            }
            
            self.send_json_response(response_data)
        except Exception as e:
            self.send_error(500, f"Error loading more text: {str(e)}")
    
    def serve_file(self, filename: str, content_type: str) -> None:
        try:
            with open(filename, 'rb') as file:
                content: bytes = file.read()
            
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, f"File {filename} not found")
        except Exception as e:
            self.send_error(500, f"Error serving file: {str(e)}")
    
    def send_json_response(self, data: Any) -> None:
        json_data: str = json.dumps(data, ensure_ascii=False)
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(json_data.encode('utf-8'))))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json_data.encode('utf-8'))
    
    def log_message(self, format: str, *args: Any) -> None:
        pass

def run_server(port: int = 8000) -> None:
    server_address: tuple[str, int] = ('', port)
    httpd: HTTPServer = HTTPServer(server_address, TypingTestHandler)
    
    print(f"Starting ORANGUTYPE web server on port {port}")
    print(f"Open your browser and navigate to: http://localhost:{port}")
    print("Press Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.shutdown()

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    run_server()
