"""Data models for skills management."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class SkillSource(str, Enum):
    """Source types for skills."""

    GITHUB = "github"
    URL = "url"
    LOCAL = "local"


class SkillMetadata(BaseModel):
    """Metadata for a skill."""

    name: str = Field(..., description="Skill name")
    description: str = Field(..., description="Skill description")
    version: str | None = Field(None, description="Skill version")
    author: str | None = Field(None, description="Skill author")
    tags: list[str] = Field(default_factory=list, description="Skill tags")
    category: str | None = Field(None, description="Skill category")
    documentation_url: str | None = Field(None, description="Documentation URL")
    repository_url: str | None = Field(None, description="Repository URL")
    icon: str | None = Field(None, description="Icon name or URL")
    dependencies: list[str] = Field(default_factory=list, description="Required dependencies")


class Skill(BaseModel):
    """Represents an external skill."""

    id: str = Field(..., description="Unique skill identifier")
    metadata: SkillMetadata = Field(..., description="Skill metadata")
    source: SkillSource = Field(..., description="Skill source type")
    source_url: str = Field(..., description="Source URL or path")
    content: dict[str, Any] | None = Field(None, description="Skill content (flow JSON, component code, etc.)")
    installed: bool = Field(False, description="Whether the skill is installed")
    installed_at: datetime | None = Field(None, description="Installation timestamp")
    last_updated: datetime | None = Field(None, description="Last update timestamp")


class SkillSearchResult(BaseModel):
    """Search result for skills."""

    skills: list[Skill] = Field(default_factory=list, description="List of matching skills")
    total: int = Field(0, description="Total number of results")
    query: str = Field("", description="Search query")


class SkillInstallRequest(BaseModel):
    """Request to install a skill."""

    source: SkillSource = Field(..., description="Skill source type")
    source_url: str = Field(..., description="Source URL or path")
    skill_name: str | None = Field(None, description="Specific skill name (for repos with multiple skills)")
    force: bool = Field(False, description="Force reinstall if already installed")


class SkillInstallResponse(BaseModel):
    """Response from skill installation."""

    success: bool = Field(..., description="Whether installation succeeded")
    skill: Skill | None = Field(None, description="Installed skill")
    message: str = Field("", description="Status message")
    errors: list[str] = Field(default_factory=list, description="Error messages if any")
