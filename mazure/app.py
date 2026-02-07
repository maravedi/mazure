"""Main FastAPI application with all routes registered.

This is the primary entry point for the mazure mock Azure API server.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .api.resource_graph_routes import router as resource_graph_router
from .api.graph_routes import router as graph_router

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Mazure - Mock Azure API",
    description="Azure Resource Manager and Microsoft Graph API mock with discovery-seeded data",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(resource_graph_router, tags=["Resource Graph"])
app.include_router(graph_router, tags=["Microsoft Graph"])


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Mazure Mock Azure API",
        "version": "2.0.0",
        "features": [
            "Azure Resource Graph queries (KQL)",
            "Microsoft Graph API (Users, Groups)",
            "Discovery-seeded state",
            "Relationship queries"
        ],
        "endpoints": {
            "resource_graph": "/providers/Microsoft.ResourceGraph/resources",
            "graph_users": "/v1.0/users",
            "graph_groups": "/v1.0/groups",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "mazure"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
