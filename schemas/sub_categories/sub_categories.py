from pydantic import BaseModel
from typing import Optional

class SubCategoriesSchema(BaseModel):
    name: str
    description: Optional[str]
    category_id: int
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    is_active: bool = True
    features_id: list[int]
    
    class Config:
        orm_mode = True