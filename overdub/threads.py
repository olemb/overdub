import threading


def start_thread(func):
    thread = threading.Thread(target=func)
    thread.daemon = True
    thread.start()
    return thread
