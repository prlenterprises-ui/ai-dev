"""
Config API endpoints for admin configuration management.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import datetime
import json

from python.database import Config, get_session

router = APIRouter(prefix="/api/configs", tags=["configs"])


class ConfigCreate(BaseModel):
    name: str
    title: str
    description: Optional[str] = None
    config_json: dict


class ConfigUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    config_json: Optional[dict] = None


@router.get("/", response_model=List[dict])
async def list_configs(session: AsyncSession = Depends(get_session)):
    """List all configurations."""
    result = await session.execute(select(Config))
    configs = result.scalars().all()
    
    return [
        {
            "id": config.id,
            "name": config.name,
            "title": config.title,
            "description": config.description,
            "config": json.loads(config.config_json),
            "created_at": config.created_at.isoformat(),
            "updated_at": config.updated_at.isoformat()
        }
        for config in configs
    ]


@router.get("/{config_name}")
async def get_config(config_name: str, session: AsyncSession = Depends(get_session)):
    """Get a specific configuration by name."""
    result = await session.execute(
        select(Config).where(Config.name == config_name)
    )
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(status_code=404, detail=f"Config '{config_name}' not found")
    
    return {
        "id": config.id,
        "name": config.name,
        "title": config.title,
        "description": config.description,
        "config": json.loads(config.config_json),
        "created_at": config.created_at.isoformat(),
        "updated_at": config.updated_at.isoformat()
    }


@router.post("/")
async def create_config(
    config_data: ConfigCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new configuration."""
    # Check if config already exists
    result = await session.execute(
        select(Config).where(Config.name == config_data.name)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=400, detail=f"Config '{config_data.name}' already exists")
    
    config = Config(
        name=config_data.name,
        title=config_data.title,
        description=config_data.description,
        config_json=json.dumps(config_data.config_json)
    )
    
    session.add(config)
    await session.commit()
    await session.refresh(config)
    
    return {
        "id": config.id,
        "name": config.name,
        "title": config.title,
        "description": config.description,
        "config": json.loads(config.config_json),
        "created_at": config.created_at.isoformat(),
        "updated_at": config.updated_at.isoformat()
    }


@router.put("/{config_name}")
async def update_config(
    config_name: str,
    config_data: ConfigUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update an existing configuration."""
    result = await session.execute(
        select(Config).where(Config.name == config_name)
    )
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(status_code=404, detail=f"Config '{config_name}' not found")
    
    if config_data.config_json is not None:
        config.config_json = json.dumps(config_data.config_json)
    if config_data.title is not None:
        config.title = config_data.title
    if config_data.description is not None:
        config.description = config_data.description
    
    config.updated_at = datetime.now()
    
    await session.commit()
    await session.refresh(config)
    
    return {
        "id": config.id,
        "name": config.name,
        "title": config.title,
        "description": config.description,
        "config": json.loads(config.config_json),
        "created_at": config.created_at.isoformat(),
        "updated_at": config.updated_at.isoformat()
    }


@router.delete("/{config_name}")
async def delete_config(
    config_name: str,
    session: AsyncSession = Depends(get_session)
):
    """Delete a configuration."""
    result = await session.execute(
        select(Config).where(Config.name == config_name)
    )
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(status_code=404, detail=f"Config '{config_name}' not found")
    
    await session.delete(config)
    await session.commit()
    
    return {"message": f"Config '{config_name}' deleted successfully"}
