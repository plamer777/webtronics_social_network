"""This is a main file to start the application"""
from fastapi import FastAPI
from starlette.responses import RedirectResponse
from routers.user_router import user_router
from routers.post_router import post_router
from settings import API_TITLE, DESCRIPTION_FILE, API_VERSION
from utils import create_path, read_from_file
from settings import AVA_ROOT, PICTURE_ROOT
# ---------------------------------------------------------------------------
app = FastAPI(
    title=API_TITLE, description=read_from_file(DESCRIPTION_FILE),
    version=API_VERSION)
app.include_router(user_router)
app.include_router(post_router)
create_path(AVA_ROOT)
create_path(PICTURE_ROOT)
# ---------------------------------------------------------------------------


@app.get('/', response_class=RedirectResponse)
async def index():
    """This view serves to redirect requests from root route to /docs with a
    swagger documentation"""
    return '/docs'
