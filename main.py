from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse

from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

template = Jinja2Templates(directory="templates")
app = FastAPI()

@app.get("/")
async def get(request: Request):
    return template.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", port=9090, reload=True)