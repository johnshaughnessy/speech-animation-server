from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Routers
from speech.api.routes.websockets import router as websocket_router


def create_app(path_client: str):

    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(websocket_router)

    app.mount(
        "/",
        StaticFiles(directory=path_client, html=True),
        name="static",
    )

    return app
