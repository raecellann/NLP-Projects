from __future__ import annotations
import os
import sys
import time
import webbrowser
import pickle
from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import Dict, List


PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
CORPORA_DIR = os.path.join(PROJECT_DIR, 'corpora')
PICKLE_PATH = os.path.join(CORPORA_DIR, 'corpora.pkl')
JS_EXPORT_PATH = os.path.join(PROJECT_DIR, 'corpora.js')


def _read_corpus_lines(txt_path: str) -> List[str]:
    lines: List[str] = []
    if not os.path.exists(txt_path):
        return lines
    with open(txt_path, 'r', encoding='utf-8') as f:
        for raw in f.readlines():
            text = raw.strip()
            if text:
                lines.append(text)
    return lines


def build_corpora_cache(force_rebuild: bool = False) -> Dict[str, List[str]]:
    """Load corpora from text files, cache them with pickle, and emit a corpora.js file.

    Returns the corpora dictionary with keys: 'easy', 'medium', 'hard'.
    """
    os.makedirs(CORPORA_DIR, exist_ok=True)

    txt_files = {
        'easy': os.path.join(CORPORA_DIR, 'short-texts.txt'),
        'medium': os.path.join(CORPORA_DIR, 'medium-texts.txt'),
        'hard': os.path.join(CORPORA_DIR, 'long-texts.txt'),
    }

    # Determine whether the pickle is stale
    pickle_mtime = os.path.getmtime(PICKLE_PATH) if os.path.exists(PICKLE_PATH) else -1
    latest_txt_mtime = max((os.path.getmtime(p) for p in txt_files.values() if os.path.exists(p)), default=-1)

    should_rebuild = force_rebuild or (pickle_mtime < latest_txt_mtime) or not os.path.exists(PICKLE_PATH)

    if should_rebuild:
        corpora: Dict[str, List[str]] = {
            'easy': _read_corpus_lines(txt_files['easy']),
            'medium': _read_corpus_lines(txt_files['medium']),
            'hard': _read_corpus_lines(txt_files['hard']),
        }
        # Fallbacks if any corpus is missing
        if not corpora['easy']:
            corpora['easy'] = [
                'Practice makes perfect',
                'Keep typing to improve',
                'Short sentences help beginners'
            ]
        if not corpora['medium']:
            corpora['medium'] = [
                'Typing regularly strengthens muscle memory and boosts your confidence while writing.',
                'Consistency and accuracy go hand in hand when aiming for higher words per minute.'
            ]
        if not corpora['hard']:
            corpora['hard'] = [
                'Developing exceptional typing proficiency requires sustained focus, deliberate practice, and carefully structured drills over long passages of varied prose.',
            ]

        with open(PICKLE_PATH, 'wb') as pf:
            pickle.dump(corpora, pf)
    else:
        with open(PICKLE_PATH, 'rb') as pf:
            corpora = pickle.load(pf)

    # Emit a tiny JS module for the frontend (no API needed)
    js_content = 'window.CORPORA = ' + __import__('json').dumps(corpora, ensure_ascii=False) + ';\n'
    with open(JS_EXPORT_PATH, 'w', encoding='utf-8') as jsf:
        jsf.write(js_content)

    return corpora


class StaticHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path: str) -> str:
        # Serve files relative to the project directory
        path = super().translate_path(path)
        # Ensure our working directory is PROJECT_DIR so relative serves are correct
        return path

    def log_message(self, format: str, *args) -> None:
        # Silence default logging for cleaner console
        pass


def run(port: int = 8000, open_browser: bool = True) -> None:
    os.chdir(PROJECT_DIR)
    build_corpora_cache()

    httpd = HTTPServer(('', port), StaticHandler)
    url = f'http://localhost:{port}'
    print('===============================================')
    print('ORANGUTYPE server running')
    print(f'Open: {url}')
    print('Ctrl+C to stop')
    print('===============================================')

    if open_browser:
        # Small delay so the server is ready before opening
        try:
            webbrowser.open(url)
        except Exception:
            pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down...')
        httpd.shutdown()


if __name__ == '__main__':
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    run(port=port, open_browser=True)


