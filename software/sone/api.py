from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from . import __title__, __version__
from .kfive import KFive
from .sone import SOne
from .models import Status, SaunaID, HTTPError


sone = SOne.instance()
kfive = KFive.instance()
# TODO: bind event handlers

app = FastAPI(
    title=__title__,
    version=__version__,
    description="REST API for sauna status fetching and control")

root_router = APIRouter(prefix="/sauna")
ping_router = APIRouter(
    tags=["Sauna Discovery"])
status_router = APIRouter(
    tags=["Sauna Status"],
    responses={404: {"description": "Sauna ID not found", "model": HTTPError}})


@ping_router.get("/ping", response_model=SaunaID)
async def get_sauna_id():
    return SaunaID(sauna_id=sone.sauna_id, model_name=sone.model_name)


@status_router.get("/{sauna_id}/status", response_model=Status)
async def get_sauna_status(sauna_id: str):
    if sauna_id != sone.sauna_id:
        raise HTTPException(status_code=404, detail="Sauna ID does not exist")
    return sone.status

root_router.include_router(ping_router)
root_router.include_router(status_router)
app.include_router(root_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
