import hmac
import hashlib

def verify_telegram_data(init_data: str, bot_token: str) -> bool:
    """Верификация данных от Telegram WebApp"""
    try:
        data = {}
        for pair in init_data.split('&'):
            key, value = pair.split('=')
            data[key] = value
        
        hash_str = data.pop('hash')
        data_str = '\n'.join(f"{k}={v}" for k, v in sorted(data.items()))
        
        secret = hashlib.sha256(bot_token.encode()).digest()
        computed_hash = hmac.new(secret, data_str.encode(), hashlib.sha256).hexdigest()
        
        return hmac.compare_digest(computed_hash, hash_str)
    except Exception:
        return False