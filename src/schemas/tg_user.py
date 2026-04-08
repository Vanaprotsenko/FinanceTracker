from pydantic import BaseModel

class SaveTgUser(BaseModel):
    name: str