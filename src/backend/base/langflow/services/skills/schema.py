"""Schema definitions for the Skills service."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SkillMetadata(BaseModel):
    """Metadata for a skill."""

    name: str
    description: str | None = None
    version: str | None = None
    author: str | None = None
    tags: list[str] | None = None
    updated_at: datetime | None = None
    repo_url: str | None = None
    install_command: str | None = None


class SkillContent(BaseModel):
    """Content of a skill."""

    raw_content: str
    markdown: str | None = None
    instructions: str | None = None
    examples: list[str] | None = None


class Skill(BaseModel):
    """Complete skill definition."""

    id: str = Field(..., description="Unique identifier for the skill (e.g., 'owner/repo/skill-name')")
    metadata: SkillMetadata
    content: SkillContent
    source: str = Field(default="github", description="Source of the skill (github, url, etc.)")


class SkillSearchRequest(BaseModel):
    """Request model for searching skills."""

    query: str | None = None
    tags: list[str] | None = None
    source: str | None = None
    limit: int = 20
    offset: int = 0


class SkillSearchResponse(BaseModel):
    """Response model for skill search results."""

    total: int
    skills: list[Skill]
    offset: int
    limit: int


class SkillInstallRequest(BaseModel):
    """Request model for installing a skill."""

    skill_id: str = Field(..., description="Skill identifier (e.g., 'owner/repo/skill-name')")
    source: str = Field(default="github", description="Source of the skill")


class SkillInstallResponse(BaseModel):
    """Response model for skill installation."""

    skill_id: str
    status: str
    message: str | None = None
    skill: Skill | None = None
