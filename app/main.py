import logging
from fastapi import Depends, FastAPI, Request, Response

from fastapi.middleware.cors import CORSMiddleware

from starlette.exceptions import HTTPException



from .src.routers.api import router as router_api

from .src.database import engine, SessionLocal, Base

from .src.config import API_PREFIX, ALLOWED_HOSTS

from .src.routers.handlers.http_error import http_error_handler

from contextlib import asynccontextmanager

from sqlalchemy import text
###
# Main application file
###


def get_application() -> FastAPI:
    ''' Configure, start and return the application '''
    
    ## Start FastApi App 
    application = FastAPI()
    session = SessionLocal()
    session.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    session.commit()
    session.close()
    ## Generate database tables
    Base.metadata.create_all(bind=engine)

    ## Mapping api routes
    application.include_router(router_api, prefix=API_PREFIX)

    ## Add exception handlers
    application.add_exception_handler(HTTPException, http_error_handler)

    ## Allow cors
    application.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_HOSTS or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    
    return application


app = get_application()


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    '''
    The middleware we'll add (just a function) will create
    a new SQLAlchemy SessionLocal for each request, add it to
    the request and then close it once the request is finished.
    '''
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response

