import random
import string
from datetime import datetime

def generate_transaction_id(length: int = 4) -> str:
    chars = string.ascii_uppercase + string.digits
    random_part = ''.join(random.choices(chars, k=length))
    timestamp = datetime.utcnow().strftime("%y%m%d%H%M")  # YYMMDDHHMM (10 chars)
    return f"{timestamp}{random_part}"
