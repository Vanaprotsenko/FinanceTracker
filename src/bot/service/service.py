import os
import logging
from typing import Dict
from src.bot.utils.utils import extract_data_from_messages

# Достал необходимые поля из сообщения
# И отправил их по ендпоинту для сохранения, или вызвать тулзы для этого

class TelegramService:
    def __init__(self, text_message: str):
        self.text_message = extract_data_from_messages(text_message)

    def send_text_to_endpoint_for_saving(self):
        pass


