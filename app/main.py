import logging # Import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router

# Basic Logging Configuration
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Initialize Limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

# Custom Exception Handler for SQLAlchemy errors
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"SQLAlchemyError occurred on request {request.method} {request.url}: {exc}") # Use logger
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal database error occurred. Please try again later."},
    )

app = FastAPI(
    title="Logistics Delivery Management System API",
    description="""
Backend API for a comprehensive Logistics Delivery Management System.
This platform enables users to manage shipments, track packages, handle user profiles,
submit feedback, and manage support tickets.
    """,
    version="0.1.0",
    contact={
        "name": "Logistics API Team",
        "url": "https://example.com/contact", # Placeholder URL
        "email": "support@example-logistics.com", # Placeholder email
    },
    openapi_tags=[
        {"name": "Authentication", "description": "User authentication, registration, and password recovery."},
        {"name": "User Profile Management", "description": "Operations related to user profiles."},
        {"name": "Shipment Management", "description": "Creating, tracking, and managing shipments."},
        {"name": "Pricing", "description": "Accessing pricing information and service tiers."},
        {"name": "Feedback Management", "description": "Submitting and retrieving feedback."},
        {"name": "Support Ticket Management", "description": "Managing user support tickets."},
    ]
)

# Add CORS middleware
# For development, you might use permissive origins.
# For production, specify your frontend's actual origin(s).
origins = [
    "http://localhost", # Example: Local Svelte, Vue, React dev server
    "http://localhost:3000", 
    "http://localhost:8080",
    # Add your production frontend origins here
    # "https://your-frontend-domain.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # or ["*"] for public API, but be careful
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], 
)

# Add state and exception handler for SlowAPI
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add the custom exception handler for SQLAlchemy
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)


app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup complete.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown.")

@app.get("/", summary="Root Endpoint", description="A simple welcome message indicating the API is running.")
@limiter.exempt 
async def root():
    logger.info("Root endpoint was accessed.")
    return {"message": "Welcome to the Logistics Delivery Management System API"}
