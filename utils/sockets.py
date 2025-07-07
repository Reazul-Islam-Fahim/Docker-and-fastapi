from fastapi_socketio import SocketManager
from fastapi import FastAPI

socket_app = FastAPI()  # For Socket.IO routes only
socket_manager = SocketManager(app=socket_app)

# Optional safe emit helper
async def safe_emit(event: str, data: dict, room: str = None):
    try:
        await socket_manager.emit(event, data, room=room)
    except Exception as e:
        print(f"[WebSocket Emit Error] Event: {event}, Room: {room}, Error: {e}")
