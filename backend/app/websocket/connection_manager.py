"""
WebSocket Connection Manager
Handles real-time connections for notifications, risk updates, and fraud alerts
"""
from typing import Dict, List, Set
from fastapi import WebSocket
import json
import asyncio

class ConnectionManager:
    def __init__(self):
        # user_id -> list of websocket connections
        self.active_connections: Dict[int, List[WebSocket]] = {}
        # Admin connections
        self.admin_connections: Set[WebSocket] = set()
        
    async def connect(self, websocket: WebSocket, user_id: int, is_admin: bool = False):
        """Accept and store new WebSocket connection"""
        await websocket.accept()
        
        if is_admin:
            self.admin_connections.add(websocket)
        else:
            if user_id not in self.active_connections:
                self.active_connections[user_id] = []
            self.active_connections[user_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: int, is_admin: bool = False):
        """Remove WebSocket connection"""
        if is_admin and websocket in self.admin_connections:
            self.admin_connections.remove(websocket)
        elif user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
    
    async def send_personal_message(self, message: dict, user_id: int):
        """Send message to specific user's all connections"""
        if user_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.append(connection)
            
            # Clean up disconnected sockets
            for conn in disconnected:
                self.disconnect(conn, user_id)
    
    async def broadcast_to_admins(self, message: dict):
        """Broadcast message to all admin connections"""
        disconnected = []
        for connection in self.admin_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        
        # Clean up disconnected sockets
        for conn in disconnected:
            if conn in self.admin_connections:
                self.admin_connections.remove(conn)
    
    async def broadcast_to_zone(self, message: dict, city: str, zone: str, db):
        """Broadcast to all users in a specific zone"""
        from ..models import User
        users_in_zone = db.query(User).filter(
            User.city == city,
            User.zone == zone
        ).all()
        
        for user in users_in_zone:
            await self.send_personal_message(message, user.id)
    
    async def send_notification(self, user_id: int, notification_type: str, title: str, body: str, data: dict = None):
        """Send notification to user"""
        message = {
            "type": "notification",
            "notification_type": notification_type,
            "title": title,
            "body": body,
            "data": data or {},
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.send_personal_message(message, user_id)
    
    async def send_risk_update(self, user_id: int, risk_data: dict):
        """Send real-time risk score update"""
        message = {
            "type": "risk_update",
            "risk_level": risk_data.get("risk_level"),
            "risk_score": risk_data.get("risk_score"),
            "factors": risk_data.get("risk_factors", {}),
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.send_personal_message(message, user_id)
    
    async def send_fraud_alert(self, claim_id: int, fraud_data: dict):
        """Send fraud alert to admins"""
        message = {
            "type": "fraud_alert",
            "claim_id": claim_id,
            "fraud_score": fraud_data.get("fraud_score"),
            "fraud_flags": fraud_data.get("fraud_flags", []),
            "severity": "HIGH" if fraud_data.get("fraud_score", 0) > 0.8 else "MEDIUM",
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.broadcast_to_admins(message)
    
    async def send_claim_status_update(self, user_id: int, claim_data: dict):
        """Send claim status update to user"""
        message = {
            "type": "claim_update",
            "claim_id": claim_data.get("id"),
            "status": claim_data.get("status"),
            "approved_amount": claim_data.get("approved_amount"),
            "reason": claim_data.get("approval_reason") or claim_data.get("rejection_reason"),
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.send_personal_message(message, user_id)
    
    async def send_disruption_alert(self, city: str, zone: str, disruption_data: dict, db):
        """Send disruption alert to all users in affected zone"""
        message = {
            "type": "disruption_alert",
            "trigger_type": disruption_data.get("trigger_type"),
            "severity": disruption_data.get("severity"),
            "city": city,
            "zone": zone,
            "details": disruption_data.get("details", {}),
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.broadcast_to_zone(message, city, zone, db)
    
    def get_active_users_count(self) -> int:
        """Get count of currently connected users"""
        return len(self.active_connections)
    
    def get_active_admins_count(self) -> int:
        """Get count of currently connected admins"""
        return len(self.admin_connections)

# Global connection manager instance
manager = ConnectionManager()
