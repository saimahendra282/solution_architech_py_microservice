from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List
import json

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🧠 In-memory storage
active_rooms: Dict[str, Dict] = {}               # room_id -> { name, participants }
room_connections: Dict[str, List[WebSocket]] = {}  # room_id -> list of WebSocket connections
email_sockets: Dict[str, WebSocket] = {}          # email -> WebSocket

# 📦 Room creation model
class RoomRequest(BaseModel):
    room_id: str
    name: str


# ✅ Create a room
@app.post("/create-room")
async def create_room(req: RoomRequest):
    if req.room_id in active_rooms:
        return {"status": "error", "message": "Room already exists"}

    active_rooms[req.room_id] = {
        "name": req.name,
        "participants": []
    }

    print(f"✅ Room created: {req.room_id} by {req.name}")
    return {"status": "success", "room_id": req.room_id}

@app.websocket("/ws-user/{email}")
async def personal_ws(websocket: WebSocket, email: str):
    await websocket.accept()

    # Gracefully close previous connection if already connected
    old_socket = email_sockets.get(email)
    if old_socket:
        try:
            await old_socket.close()
        except Exception:
            pass

    email_sockets[email] = websocket
    print(f"🧩 WebSocket connected: {email}")

    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)

            if data.get("type") == "call-request":
                to_email = data.get("to")
                if to_email in email_sockets:
                    await email_sockets[to_email].send_text(json.dumps(data))
                else:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": f"{to_email} is not online"
                    }))

            elif data.get("type") in ["call-accepted", "call-rejected"]:
                to_email = data.get("to")
                if to_email in email_sockets:
                    await email_sockets[to_email].send_text(json.dumps(data))

    except WebSocketDisconnect:
        print(f"❌ WebSocket disconnected: {email}")
    finally:
        # Remove only if this same socket is stored (avoid race conditions)
        if email_sockets.get(email) == websocket:
            email_sockets.pop(email, None)

# 🔍 Get room info
@app.get("/room/{room_id}")
async def get_room_info(room_id: str):
    room = active_rooms.get(room_id)
    if not room:
        return {"error": "Room not found"}
    return {"room_id": room_id, "name": room["name"]}


# 🔄 WebSocket for signaling (WebRTC)
@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()

    if room_id not in room_connections:
        room_connections[room_id] = []

    room_connections[room_id].append(websocket)
    print(f"🟢 WebSocket connected to room: {room_id}")

    # 👇 If two peers are connected, notify the first to initiate the call
    if len(room_connections[room_id]) == 2:
        try:
            await room_connections[room_id][0].send_text(json.dumps({ "type": "init-call" }))
        except Exception as e:
            print(f"⚠️ Failed to send init-call: {e}")

    try:
        while True:
            message = await websocket.receive_text()

            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                print("❌ Received non-JSON message")
                continue

            # Broadcast to all other peers in the room
            for conn in room_connections[room_id]:
                if conn != websocket:
                    try:
                        await conn.send_text(json.dumps(data))
                    except Exception as e:
                        print(f"⚠️ Failed to send to peer: {e}")

    except WebSocketDisconnect:
        print(f"🔌 Disconnected from room: {room_id}")
    finally:
        room_connections[room_id].remove(websocket)

