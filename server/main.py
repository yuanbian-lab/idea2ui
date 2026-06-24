from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.routers import chat, files
from server.config import HOST, PORT

app = FastAPI(title="idea2ui API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(files.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server.main:app", host=HOST, port=PORT, reload=True)
