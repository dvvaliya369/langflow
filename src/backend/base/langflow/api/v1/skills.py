"""API endpoints for skills management."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from loguru import logger

from langflow.services.skills.manager import SkillsManager
from langflow.services.skills.models import Skill, SkillInstallRequest, SkillInstallResponse, SkillSearchResult

router = APIRouter(prefix="/skills", tags=["Skills"])


@router.get("/search", response_model=SkillSearchResult)
async def search_skills(
    query: Annotated[str, Query(description="Search query")],
    source: Annotated[str | None, Query(description="Source filter (github, url, local)")] = None,
) -> SkillSearchResult:
    """Search for skills from external sources.

    Args:
        query: Search query
        source: Optional source filter

    Returns:
        Search results
    """
    try:
        manager = SkillsManager()
        results = await manager.search_skills(query=query, source=source)
        return results
    except Exception as e:
        logger.error(f"Error searching skills: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/install", response_model=SkillInstallResponse)
async def install_skill(request: SkillInstallRequest) -> SkillInstallResponse:
    """Install a skill from an external source.

    Args:
        request: Installation request

    Returns:
        Installation response
    """
    try:
        manager = SkillsManager()
        response = await manager.install_skill(request)
        return response
    except Exception as e:
        logger.error(f"Error installing skill: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/installed", response_model=list[Skill])
async def get_installed_skills() -> list[Skill]:
    """Get all installed skills.

    Returns:
        List of installed skills
    """
    try:
        manager = SkillsManager()
        skills = manager.get_installed_skills()
        return skills
    except Exception as e:
        logger.error(f"Error getting installed skills: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/{skill_id}", response_model=Skill)
async def get_skill(skill_id: str) -> Skill:
    """Get a specific skill by ID.

    Args:
        skill_id: Skill ID

    Returns:
        Skill details
    """
    try:
        manager = SkillsManager()
        skill = manager.get_skill(skill_id)
        if not skill:
            raise HTTPException(status_code=404, detail=f"Skill not found: {skill_id}")
        return skill
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting skill: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/{skill_id}")
async def uninstall_skill(skill_id: str) -> dict[str, str]:
    """Uninstall a skill.

    Args:
        skill_id: Skill ID

    Returns:
        Success message
    """
    try:
        manager = SkillsManager()
        success = manager.uninstall_skill(skill_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Skill not found: {skill_id}")
        return {"message": f"Skill {skill_id} uninstalled successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uninstalling skill: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/{skill_id}/update", response_model=Skill)
async def update_skill(skill_id: str) -> Skill:
    """Update an installed skill.

    Args:
        skill_id: Skill ID

    Returns:
        Updated skill
    """
    try:
        manager = SkillsManager()
        skill = manager.update_skill(skill_id)
        if not skill:
            raise HTTPException(status_code=404, detail=f"Skill not found or update failed: {skill_id}")
        return skill
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating skill: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e
