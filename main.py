from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from dataclasses import dataclass
from typing import Dict
import uuid
import json
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

template = Jinja2Templates(directory="templates")
app = FastAPI()

@dataclass
class ConnectionManager():
    def __init__(self) -> None:
        self.active_connection: dict = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        id = str(uuid.uuid4())

        self.active_connection[id] = websocket
        data = json.dumps({"isMe": True, "data": "Have joined!!", "username" :"YOU"})
        await self.send_message(websocket, data)

    async def send_message(self, ws: WebSocket, message: str):
        await ws.send_text(message)

    async def broadcast(self, ws: WebSocket, data: str):
        decoded_data = json.loads(data)
        for connection in self.active_connection.values():
            is_me = False
            if (connection == ws):
                is_me = True
            await connection.send_text(json.dumps({"isMe": is_me, "data": decoded_data['message'], "username": decoded_data['username']}))

    def find_connection_id(self, ws: WebSocket):
        websocket_list = list(self.active_connection.values())
        id_list = list(self.active_connection.keys())

        pos = websocket_list.index(ws)

        return id_list[pos]

    async def disconnect(self, ws: WebSocket):
        id = self.find_connection_id(ws)
        del self.active_connection[id]

app.mount('/static', StaticFiles(directory="static"), name="static")

connection_manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return template.TemplateResponse("index.html", {"request": request, 'title': 'Chat app 1'})

@app.websocket("/message")
async def websocket_endpoint(websocket: WebSocket):
    await connection_manager.connect(websocket)

    try:
        while True:
            # Receive the texts from the users
            data = await websocket.receive_text()
            await connection_manager.broadcast(websocket, data)
    except WebSocketDisconnect:
        return RedirectResponse("/")
    
    # await websocket.accept()
    # while True:
    #     data = await websocket.receive_text()
    #     await websocket.send_text(f"Message text was: {data}")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", port=9090, reload=True)