from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from . import __title__, __version__
from .sone import SOne
from .models import SaunaID


sone = SOne.instance()
app = FastAPI(
    title=__title__,
    version=__version__,
    description="REST API for sauna status fetching and control")

root_router = APIRouter(prefix="/sauna")
ping_router = APIRouter(tags=["Sauna Discovery"])


@ping_router.get("/ping", response_model=SaunaID)
async def get_sauna_id():
    return SaunaID(sauna_id=sone.sauna_id, model_name=sone.model_name)


root_router.include_router(ping_router)
app.include_router(root_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
