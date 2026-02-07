"""FastAPI routes for Microsoft Graph API."""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List
import logging

from ..services.graph import GraphService
from ..core.state import StateManager

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/v1.0",
    tags=["Microsoft Graph"]
)


def get_graph_service() -> GraphService:
    """Dependency injection for GraphService."""
    return GraphService(StateManager())


# ==================== Users Endpoints ====================

@router.get("/users")
async def list_users(
    top: int = Query(100, alias="$top", ge=1, le=999),
    skip: int = Query(0, alias="$skip", ge=0),
    select: Optional[str] = Query(None, alias="$select"),
    filter_expr: Optional[str] = Query(None, alias="$filter"),
    orderby: Optional[str] = Query(None, alias="$orderby"),
    service: GraphService = Depends(get_graph_service)
):
    """List users from Entra ID.
    
    GET /v1.0/users?$top=10&$skip=0&$select=displayName,mail&$filter=startswith(displayName,'John')
    
    Returns:
        OData response with user collection
    """
    select_fields = select.split(',') if select else None
    result = await service.list_users(
        top=top,
        skip=skip,
        select=select_fields,
        filter_expr=filter_expr,
        orderby=orderby
    )
    
    # Check for error response
    if 'error' in result:
        status_code = result.get('_status_code', 500)
        raise HTTPException(status_code=status_code, detail=result['error'])
    
    return result


@router.get("/users/{user_id}")
async def get_user(
    user_id: str,
    select: Optional[str] = Query(None, alias="$select"),
    service: GraphService = Depends(get_graph_service)
):
    """Get a specific user by ID or userPrincipalName.
    
    GET /v1.0/users/{id}
    GET /v1.0/users/john.doe@contoso.com
    
    Returns:
        User object
    """
    select_fields = select.split(',') if select else None
    result = await service.get_user(user_id, select=select_fields)
    
    if 'error' in result:
        status_code = result.get('_status_code', 500)
        raise HTTPException(status_code=status_code, detail=result['error'])
    
    return result


# ==================== Groups Endpoints ====================

@router.get("/groups")
async def list_groups(
    top: int = Query(100, alias="$top", ge=1, le=999),
    skip: int = Query(0, alias="$skip", ge=0),
    select: Optional[str] = Query(None, alias="$select"),
    filter_expr: Optional[str] = Query(None, alias="$filter"),
    orderby: Optional[str] = Query(None, alias="$orderby"),
    service: GraphService = Depends(get_graph_service)
):
    """List groups from Entra ID.
    
    GET /v1.0/groups?$top=10&$filter=startswith(displayName,'IT')
    
    Returns:
        OData response with group collection
    """
    select_fields = select.split(',') if select else None
    result = await service.list_groups(
        top=top,
        skip=skip,
        select=select_fields,
        filter_expr=filter_expr,
        orderby=orderby
    )
    
    if 'error' in result:
        status_code = result.get('_status_code', 500)
        raise HTTPException(status_code=status_code, detail=result['error'])
    
    return result


@router.get("/groups/{group_id}")
async def get_group(
    group_id: str,
    select: Optional[str] = Query(None, alias="$select"),
    service: GraphService = Depends(get_graph_service)
):
    """Get a specific group by ID.
    
    GET /v1.0/groups/{id}
    
    Returns:
        Group object
    """
    select_fields = select.split(',') if select else None
    result = await service.get_group(group_id, select=select_fields)
    
    if 'error' in result:
        status_code = result.get('_status_code', 500)
        raise HTTPException(status_code=status_code, detail=result['error'])
    
    return result


@router.get("/groups/{group_id}/members")
async def list_group_members(
    group_id: str,
    top: int = Query(100, alias="$top", ge=1, le=999),
    skip: int = Query(0, alias="$skip", ge=0),
    service: GraphService = Depends(get_graph_service)
):
    """List members of a group.
    
    GET /v1.0/groups/{id}/members
    
    Returns:
        OData response with directory objects (users, groups, etc.)
    """
    result = await service.list_group_members(group_id, top=top, skip=skip)
    
    if 'error' in result:
        status_code = result.get('_status_code', 500)
        raise HTTPException(status_code=status_code, detail=result['error'])
    
    return result


# ==================== Health Check ====================

@router.get("/")
async def graph_root():
    """Root endpoint for Graph API."""
    return {
        'service': 'Microsoft Graph API (Mock)',
        'version': 'v1.0',
        'endpoints': [
            '/v1.0/users',
            '/v1.0/groups',
            '/v1.0/groups/{id}/members'
        ]
    }
