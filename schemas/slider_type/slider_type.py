from pydantic import BaseModel

class SliderTypeSchema(BaseModel):
    type: str
    description: str | None = None
    rate: float
    height: int
    width: int
    is_active: bool = True

    class Config:
        orm_mode = True