import hashlib

def generate_cache_key(prompt: str):
    return hashlib.md5(prompt.encode()).hexdigest()