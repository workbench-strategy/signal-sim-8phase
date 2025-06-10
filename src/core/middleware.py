# src/core/middleware.py

def middleware(func):
    def wrapper(*args, **kwargs):
        print("[Middleware] Before call")
        result = func(*args, **kwargs)
        print("[Middleware] After call")
        return result
    return wrapper
