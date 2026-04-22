import os
import io
import base64
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
import logging
from openai import AsyncOpenAI


class LLMService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"
        self.prompts_paths = Path(__file__).resolve().parent / "prompts" / "analyze_the_bill.txt"
        self.logger = logging.getLogger(__name__)

    def _get_prompt(self) -> str:
        with open(self.prompts_paths, "r", encoding="utf-8") as file:
            prompt = file.read()
        return prompt

    @staticmethod
    def optimize_image_for_gpt_base64(image_bytes: bytes):
        np_arr = np.frombuffer(image_bytes, dtype=np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Invalid image payload")

        h, w = img.shape[:2]
        roi = img[:, int(w * 0.3):int(w * 0.95)]

        target_width = 400
        roi = cv2.resize(roi, (target_width, int(target_width * roi.shape[0] / roi.shape[1])))
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        pil_img = Image.fromarray(gray)
        buffer = io.BytesIO()
        pil_img.save(buffer, format="JPEG", quality=10)

        return base64.b64encode(buffer.getvalue()).decode()

    async def get_price_from_llm_service(self, image: bytes):
        image = self.optimize_image_for_gpt_base64(image)
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text",
                         "text": self._get_prompt()},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image}",
                                "detail": "low"
                            }
                        }
                    ]
                }
            ],
            max_tokens=50,
        )
        content = response.choices[0].message.content
        self.logger.info(f"LLM service response: {content}")
        return content
