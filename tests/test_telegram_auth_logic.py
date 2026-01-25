
import os
import hmac
import hashlib
import json
import time
from urllib.parse import urlencode

# Mocking the environment
os.environ["TOKEN_BOT"] = "123456789:ABCdefGHIjklMNOpqrSTUvwxYZ"
BOT_TOKEN = os.environ["TOKEN_BOT"]

def generate_mock_init_data(user_id, username):
    user_data = {
        "id": user_id,
        "first_name": "Test",
        "last_name": "User",
        "username": username,
        "language_code": "en"
    }
    data = {
        "auth_date": int(time.time()),
        "query_id": "AAHdF6IQAAAAAN0XohD9V_z6",
        "user": json.dumps(user_data, separators=(',', ':'))
    }
    
    # Sort data for check string
    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(data.items())
    )
    
    # Calculate hash
    secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()
    
    data["hash"] = calculated_hash
    return urlencode(data)

def test_verification_logic():
    from src.bot.utils.utils import verify_telegram_init_data
    
    user_id = 5334960289
    username = "test_user"
    init_data = generate_mock_init_data(user_id, username)
    print(f"Generated initData: {init_data}")
    
    try:
        verified_data = verify_telegram_init_data(init_data)
        print("✅ Verification successful!")
        user = json.loads(verified_data["user"])
        assert user["id"] == user_id
        assert user["username"] == username
        print("✅ Data integrity verified!")
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        exit(1)

if __name__ == "__main__":
    test_verification_logic()
