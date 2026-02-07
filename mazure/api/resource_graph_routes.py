"""FastAPI routes for Azure Resource Graph queries."""

from fastapi import APIRouter, Depends, Body, Query
from typing import Dict, Any, List, Optional
import logging

from ..services.resource_graph import ResourceGraphService
from ..core.state import StateManager

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/providers/Microsoft.ResourceGraph",
    tags=["Resource Graph"]
)


def get_resource_graph_service() -> ResourceGraphService:
    """Dependency injection for ResourceGraphService."""
    return ResourceGraphService(StateManager())


@router.post("/resources")
async def query_resources(
    payload: Dict[str, Any] = Body(...),
    api_version: str = Query("2021-03-01", alias="api-version"),
    service: ResourceGraphService = Depends(get_resource_graph_service)
):
    """Azure Resource Graph query endpoint.
    
    POST /providers/Microsoft.ResourceGraph/resources?api-version=2021-03-01
    
    Request Body:
    {
        "subscriptions": ["sub-id-1", "sub-id-2"],
        "query": "Resources | where type =~ 'Microsoft.Compute/virtualMachines' | take 10",
        "options": {
            "$skip": 0,
            "$top": 100
        }
    }
    
    Response:
    {
        "totalRecords": 42,
        "count": 10,
        "data": [...],
        "facets": [],
        "resultTruncated": "false"
    }
    """
    try:
        subscriptions = payload.get('subscriptions', [])
        query = payload.get('query', 'Resources')
        options = payload.get('options', {})
        
        if not subscriptions:
            return {
                'error': {
                    'code': 'BadRequest',
                    'message': 'At least one subscription must be provided'
                }
            }
        
        result = await service.query(subscriptions, query, options)
        return result
        
    except ValueError as e:
        logger.warning(f"Invalid query: {str(e)}")
        return {
            'error': {
                'code': 'InvalidQuery',
                'message': str(e)
            }
        }
    except Exception as e:
        logger.error(f"Query execution failed: {str(e)}")
        return {
            'error': {
                'code': 'InternalServerError',
                'message': 'An error occurred while executing the query'
            }
        }


@router.get("/resources")
async def query_resources_get(
    subscriptions: List[str] = Query(...),
    query: str = Query("Resources"),
    api_version: str = Query("2021-03-01", alias="api-version"),
    service: ResourceGraphService = Depends(get_resource_graph_service)
):
    """GET version of Resource Graph query (less common but supported)."""
    try:
        result = await service.query(subscriptions, query, {})
        return result
    except Exception as e:
        logger.error(f"Query execution failed: {str(e)}")
        return {
            'error': {
                'code': 'InternalServerError',
                'message': str(e)
            }
        }
