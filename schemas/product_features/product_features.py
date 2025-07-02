from pydantic import BaseModel

class ProductFeaturesSchema(BaseModel):
    name: str
    unit: str
    value: str
    is_active: bool
    
    class Config:
        orm_mode = True
