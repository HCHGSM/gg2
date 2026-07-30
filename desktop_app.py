import subprocess
import sys
import os
import webbrowser
import threading
import time

def start_server_and_gui():
    # Start the server in background thread
    from enterprise_erp.core.engine import init_enterprise_db
    import uvicorn
    
    init_enterprise_db()
    
    def run_uvicorn():
        uvicorn.run("enterprise_erp.api.server:app", host="127.0.0.1", port=8080, log_level="error")

    t = threading.Thread(target=run_uvicorn, daemon=True)
    t.start()

    # Wait 1 second for server startup
    time.sleep(1.5)

    # Open system browser as a desktop app window
    url = "http://127.0.0.1:8080"
    print(f"جاري فتح التطبيق على الرابط: {url}")
    webbrowser.open(url)

if __name__ == '__main__':
    start_server_and_gui()
    # Keep process alive
    while True:
        time.sleep(1)
