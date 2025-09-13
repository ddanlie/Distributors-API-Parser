#TODO: 
# Crucial:
# Bitrix authentication integration
# Set up nginx public folder
# Close 8000 port (access to this app should be only using nginx)
# Define requests limitations
# Define roles: e.g. only admin can send Purchase Orders, See invoices
# Define tech stack: nginx, uvicorn, python 3.10+ fastapi, tailwind, jinja2, axios 

# Code notes
# HTML Routing: <a href="/route"> <button> Go there </button> </a>

# Set up logger

#Bitrix sends post request 
#with credentials when app is opened

import os

#this import has to be the first
from .boot import boot #pyright: ignore

boot()

from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from parser.core.endpoints import app_router, api_router

from parser.logger.logger import get_parser_logger

logger = get_parser_logger()

app = FastAPI()

#FIXME - no idea what to do with CORS, do research
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(app_router,  prefix="/app")
app.include_router(api_router,  prefix="/api")

logger.info("FastAPI app initialized, routers included")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)