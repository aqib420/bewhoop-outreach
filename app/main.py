from fastapi import FastAPI
from app.api.v1 import email_routes
from app.db import models
from app.db.database import engine
import logging

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)


app = FastAPI(
    title="BeWhoop Email Outreach API",
    version="1.0.0",
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",     # ReDoc
)

# Register routers
app.include_router(email_routes.router, prefix="/api/v1", tags=["Email"])