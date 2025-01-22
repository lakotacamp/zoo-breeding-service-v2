# main.py

import logging
from fastapi import FastAPI

# If you want to load environment config (like a database URL), you can do:
# from app.settings import settings  # (optional, if you have it)

# Routers
from app.routers.animals import router as animals_router
from app.routers.breeding import router as breeding_router
from app.routers.litter import router as litter_router
from app.routers.offspring import router as offspring_router
from app.routers.mortality import router as mortality_router
from app.routers.rehoming import router as rehoming_router
from app.routers.alerts import router as alerts_router
from app.routers.family_tree import router as family_tree_router

# Initialization
from app.services.breeding_service import initialize_data

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

def create_app() -> FastAPI:
    """
    Application factory: creates the FastAPI app, includes all routers,
    and runs any needed initialization.
    """
    # 1) Create the app
    application = FastAPI(
        title="Zoo Breeding Service API",
        description="An API for managing breeding, litters, offspring logs, rehoming, etc.",
        version="1.0.0",
    )

    # 2) Initialize data (if needed)
    initialize_data()

    # 3) Include routers
    application.include_router(animals_router)
    application.include_router(breeding_router)
    application.include_router(litter_router)
    application.include_router(offspring_router)
    application.include_router(mortality_router)
    application.include_router(rehoming_router)
    application.include_router(alerts_router)
    application.include_router(family_tree_router)

    return application

# Create the global app for your entrypoint (e.g., uvicorn starts here):
app = create_app()
