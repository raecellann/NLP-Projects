#!/usr/bin/env python3
import json
import time
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from backend import TypingTest, NGramModel, get_test_text, get_multiple_texts, submit_test_results, get_corpus_stats

typing_test = TypingTest()

class TypingTestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        
        self.send_cors_headers()
        
        if path == '/':
            self.serve_file('index.html', 'text/html')
        elif path == '/api/text':
            use_ngrams = query_params.get('use_ngrams', ['true'])[0].lower() == 'true'
            length = int(query_params.get('length', ['30'])[0])
            
            text = get_test_text(use_ngrams, length)
            self.send_json_response({'text': text})
            
        elif path == '/api/texts':
            count = int(query_params.get('count', ['5'])[0])
            use_ngrams = query_params.get('use_ngrams', ['true'])[0].lower() == 'true'
            length = int(query_params.get('length', ['30'])[0])
            
            texts = get_multiple_texts(count, use_ngrams, length)
            self.send_json_response({'texts': texts})
            
        elif path == '/api/corpus-stats':
            stats = get_corpus_stats()
            self.send_json_response(stats)
            
        elif path == '/api/ngrams':
            length = int(query_params.get('length', ['20'])[0])
            ngram_text = typing_test.ngram_model.generate_text(length)
            random_text = typing_test.ngram_model.generate_random_text(length)
            
            self.send_json_response({
                'ngram_text': ngram_text,
                'random_text': random_text,
                'corpus_stats': get_corpus_stats()
            })
            
        elif path.endswith('.css'):
            self.serve_file(path[1:], 'text/css')
        elif path.endswith('.js'):
            self.serve_file(path[1:], 'application/javascript')
        elif path.endswith('.png') or path.endswith('.jpg') or path.endswith('.jpeg') or path.endswith('.gif'):
            self.serve_file(path[1:], 'image/png')
        else:
            try:
                self.serve_file(path[1:], 'text/plain')
            except FileNotFoundError:
                self.send_error(404, 'File not found')
    
    def do_POST(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        self.send_cors_headers()
        
        if path == '/api/results':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                original_text = data.get('original_text', '')
                typed_text = data.get('typed_text', '')
                time_taken = data.get('time_taken', 0)
                
                results = submit_test_results(original_text, typed_text, time_taken)
                self.send_json_response(results)
                
            except json.JSONDecodeError:
                self.send_error(400, 'Invalid JSON data')
            except Exception as e:
                self.send_error(500, f'Server error: {str(e)}')
        else:
            self.send_error(404, 'Endpoint not found')
    
    def do_OPTIONS(self):
        self.send_cors_headers()
        self.end_headers()
    
    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Max-Age', '86400')
    
    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        
        json_data = json.dumps(data, ensure_ascii=False)
        self.wfile.write(json_data.encode('utf-8'))
    
    def serve_file(self, file_path, content_type):
        try:
            with open(file_path, 'rb') as file:
                content = file.read()
                
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(content)))
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(content)
            
        except FileNotFoundError:
            self.send_error(404, 'File not found')
        except Exception as e:
            self.send_error(500, f'Server error: {str(e)}')
    
    def log_message(self, format, *args):
        pass

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, TypingTestHandler)
    
    print(f"🚀 Starting WPM Typing Test Server...")
    print(f"📁 Serving files from: {os.getcwd()}")
    print(f"🌐 Server running at: http://localhost:{port}")
    print(f"📊 API endpoints available:")
    print(f"   GET  /api/text - Get random text for typing test")
    print(f"   GET  /api/texts - Get multiple texts for continuous typing")
    print(f"   GET  /api/corpus-stats - Get corpus statistics")
    print(f"   GET  /api/ngrams - Test n-gram generation")
    print(f"   POST /api/results - Submit test results")
    print(f"")
    print(f"💡 Open your browser and go to: http://localhost:{port}")
    print(f"⏹️  Press Ctrl+C to stop the server")
    print(f"=" * 60)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"\n🛑 Server stopped by user")
        httpd.server_close()
        print(f"👋 Goodbye!")

if __name__ == '__main__':
    print("🧪 Testing Backend Integration...")
    try:
        print("📚 Loading corpus data...")
        stats = get_corpus_stats()
        print(f"   Corpus loaded: {stats['total_words']} words, {stats['unique_words']} unique")
        
        print("📝 Testing text generation...")
        text = get_test_text(use_ngrams=True, length=20)
        print(f"   Generated text: {text[:50]}...")
        
        print("✅ Backend test completed successfully!")
        print("")
        
    except Exception as e:
        print(f"⚠️  Backend test failed: {e}")
        print("   Continuing with server startup...")
        print("")
    
    run_server() 