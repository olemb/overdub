import threading

def start_thread(func):
    thread = threading.Thread(target=func)
    thread.setDaemon(True)
    thread.start()
    return thread
