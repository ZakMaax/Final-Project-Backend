import uvicorn
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.properties import property_router
from routes.users import user_router
from routes.auth import auth_router
from routes.contact import contact_router
from contextlib import asynccontextmanager
from core.init_db import init_db
import os

version = "v1"


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("The server is starting up")
    await init_db()
    yield
    print("The server is shutting down")


app = FastAPI(
    lifespan=lifespan,
    title="This is the Guryasamo Real estate API",
    description="A RESTAPI built on FastAPI for the Guryasamo Real Estate application",
    version=version,
)


uploads_path = os.path.join(os.path.dirname(__file__), "uploads")
app.mount("/uploads", StaticFiles(directory=uploads_path), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    property_router, prefix=f"/api/{version}/properties", tags=["properties"]
)
app.include_router(user_router, prefix=f"/api/{version}/users", tags=["users"])
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["auth"])
app.include_router(contact_router, prefix=f"/api/{version}", tags=["contact"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
