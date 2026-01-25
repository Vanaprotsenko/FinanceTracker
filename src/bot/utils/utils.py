import os
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
