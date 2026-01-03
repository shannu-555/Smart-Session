# Manages WebSocket connections for student and teacher clients
# Tracks active connections and broadcasts state updates

from typing import Set
from fastapi import WebSocket


class WebSocketManager:
    def __init__(self):
        self.student_connections: Set[WebSocket] = set()
        self.teacher_connections: Set[WebSocket] = set()

    async def connect_student(self, websocket: WebSocket):
        await websocket.accept()
        self.student_connections.add(websocket)

    async def connect_teacher(self, websocket: WebSocket):
        await websocket.accept()
        self.teacher_connections.add(websocket)

    def disconnect_student(self, websocket: WebSocket):
        self.student_connections.discard(websocket)

    def disconnect_teacher(self, websocket: WebSocket):
        self.teacher_connections.discard(websocket)

    async def broadcast_to_teachers(self, message: dict):
        # Send state updates to all connected teacher dashboards
        disconnected = set()
        for connection in self.teacher_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect_teacher(connection)

