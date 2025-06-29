from fastapi_socketio import SocketManager

socket_manager = None  


async def safe_emit(event: str, data: dict, room: str = None):
    try:
        await socket_manager.emit(event, data, room=room)
    except Exception as e:
        print(f"[WebSocket Emit Error] Event: {event}, Room: {room}, Error: {e}")
