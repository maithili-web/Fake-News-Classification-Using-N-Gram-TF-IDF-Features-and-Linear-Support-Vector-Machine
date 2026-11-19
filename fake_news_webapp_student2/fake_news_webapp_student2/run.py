"""Start the web app: python run.py"""
import threading
import webbrowser

import uvicorn

URL = 'http://127.0.0.1:8000'

if __name__ == '__main__':
    threading.Timer(1.5, webbrowser.open, args=(URL,)).start()
    print(f'IFND Headline Checker is running at {URL} (press Ctrl+C to stop)')
    uvicorn.run('app.main:app', host='127.0.0.1', port=8000)
