import os
import re
import hmac
import hashlib
from urllib.parse import parse_qsl
from datetime import datetime, timezone

BOT_TOKEN = os.getenv("TOKEN_BOT")

def verify_telegram_init_data(init_data: str) -> dict:
    data = dict(parse_qsl(init_data, strict_parsing=True))

    if "hash" not in data:
        raise ValueError("No hash in initData")

    received_hash = data.pop("hash")

    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(data.items())
    )

    secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()

    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        raise ValueError("Invalid Telegram signature")

    auth_date = int(data.get("auth_date", 0))
    now = int(datetime.now(tz=timezone.utc).timestamp())

    if now - auth_date > 86400:
        raise ValueError("Telegram auth expired")

    return data

def extract_data_from_messages(text: str) -> dict:
    # Pattern: [amount] [description] [optional currency]
    # Examples: 
    # "100 Coffee" -> amount=100, description=Coffee, currency=USD
    # "50.5 Taxi EUR" -> amount=50.5, description=Taxi, currency=EUR
    data = {"amount": 0.0, "description": "Unknown", "currency": "USD"}
    
    parts = text.split()
    if not parts:
        return {}

    try:
        # Try to find amount (first numeric-ish part)
        for i, part in enumerate(parts):
            clean_part = part.replace(',', '.')
            if re.match(r"^-?\d+(\.\d+)?$", clean_part):
                data["amount"] = float(clean_part)
                
                # Assume next part is description
                if i + 1 < len(parts):
                    data["description"] = parts[i+1]
                
                # Assume part after that is currency (if 3 letters)
                if i + 2 < len(parts):
                    potential_currency = parts[i+2].upper()
                    if len(potential_currency) == 3:
                        data["currency"] = potential_currency
                
                return data
                
        # Fallback if no clear numeric part found
        return {}
    except Exception:
        return {}

