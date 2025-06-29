from pydantic import BaseModel
from models.notifications.notifications import NotificationType

class NotificationsSchema(BaseModel):
    user_id : int
    message: str
    type: NotificationType
    is_read: bool = False
    
    class Config:
        orm_mode = True