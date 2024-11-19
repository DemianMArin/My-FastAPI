from pydantic import BaseModel

class Teacher(BaseModel):
    text: str
    expression: list
