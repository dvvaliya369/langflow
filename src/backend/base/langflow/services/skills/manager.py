"""Skills manager for discovering, installing, and managing external skills."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx
from loguru import logger

from langflow.services.skills.models import (
    Skill,
    SkillInstallRequest,
    SkillInstallResponse,
    SkillMetadata,
    SkillSearchResult,
    SkillSource,
)


class SkillsManager:
    """Manager for external skills integration."""

    def __init__(self, skills_dir: Path | None = None):
        """Initialize the skills manager.

        Args:
            skills_dir: Directory to store installed skills. Defaults to ~/.langflow/skills
        """
        if skills_dir is None:
            from langflow.services.settings.constants import DEFAULT_LANGFLOW_DIR

            skills_dir = Path(DEFAULT_LANGFLOW_DIR) / "skills"

        self.skills_dir = Path(skills_dir)
        self.skills_dir.mkdir(parents=True, exist_ok=True)

        self.index_file = self.skills_dir / "index.json"
        self._load_index()

    def _load_index(self) -> None:
        """Load the skills index from disk."""
        if self.index_file.exists():
            try:
                with open(self.index_file) as f:
                    data = json.load(f)
                    self.installed_skills = {
                        skill_id: Skill.model_validate(skill_data) for skill_id, skill_data in data.items()
                    }
            except Exception as e:
                logger.warning(f"Failed to load skills index: {e}")
                self.installed_skills = {}
        else:
            self.installed_skills = {}

    def _save_index(self) -> None:
        """Save the skills index to disk."""
        try:
            data = {skill_id: skill.model_dump(mode="json") for skill_id, skill in self.installed_skills.items()}
            with open(self.index_file, "w") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save skills index: {e}")

    def _generate_skill_id(self, source_url: str, skill_name: str | None = None) -> str:
        """Generate a unique skill ID.

        Args:
            source_url: Source URL
            skill_name: Optional skill name

        Returns:
            Unique skill ID
        """
        key = f"{source_url}:{skill_name or ''}"
        return hashlib.sha256(key.encode()).hexdigest()[:16]

    async def search_skills(self, query: str, source: str | None = None) -> SkillSearchResult:
        """Search for skills from various sources.

        Args:
            query: Search query
            source: Optional source filter (github, url, local)

        Returns:
            Search results
        """
        results: list[Skill] = []

        # Search in installed skills
        for skill in self.installed_skills.values():
            if self._matches_query(skill, query):
                results.append(skill)

        # Search GitHub repositories (example: vercel-labs/skills)
        if source is None or source == "github":
            github_results = await self._search_github_skills(query)
            results.extend(github_results)

        return SkillSearchResult(skills=results, total=len(results), query=query)

    def _matches_query(self, skill: Skill, query: str) -> bool:
        """Check if a skill matches the search query.

        Args:
            skill: Skill to check
            query: Search query

        Returns:
            True if skill matches query
        """
        query_lower = query.lower()
        return (
            query_lower in skill.metadata.name.lower()
            or query_lower in skill.metadata.description.lower()
            or any(query_lower in tag.lower() for tag in skill.metadata.tags)
        )

    async def _search_github_skills(self, query: str) -> list[Skill]:
        """Search for skills in GitHub repositories.

        Args:
            query: Search query

        Returns:
            List of matching skills
        """
        results: list[Skill] = []

        # Known skill repositories
        skill_repos = [
            "vercel-labs/skills",
            "langflow-ai/langflow-skills",  # Placeholder for future official repo
        ]

        async with httpx.AsyncClient(timeout=30.0) as client:
            for repo in skill_repos:
                try:
                    skills = await self._fetch_github_repo_skills(client, repo)
                    for skill in skills:
                        if self._matches_query(skill, query):
                            results.append(skill)
                except Exception as e:
                    logger.debug(f"Failed to fetch skills from {repo}: {e}")

        return results

    async def _fetch_github_repo_skills(self, client: httpx.AsyncClient, repo: str) -> list[Skill]:
        """Fetch skills from a GitHub repository.

        Args:
            client: HTTP client
            repo: Repository in format owner/repo

        Returns:
            List of skills
        """
        skills: list[Skill] = []

        try:
            # Fetch repository contents
            api_url = f"https://api.github.com/repos/{repo}/contents"
            response = await client.get(api_url)
            response.raise_for_status()
            contents = response.json()

            # Look for skills directory
            skills_dir = None
            for item in contents:
                if item["name"] == "skills" and item["type"] == "dir":
                    skills_dir = item["url"]
                    break

            if not skills_dir:
                return skills

            # Fetch skills directory contents
            response = await client.get(skills_dir)
            response.raise_for_status()
            skill_items = response.json()

            # Process each skill
            for item in skill_items:
                if item["type"] == "dir":
                    skill = await self._parse_github_skill(client, repo, item["name"], item["url"])
                    if skill:
                        skills.append(skill)

        except Exception as e:
            logger.debug(f"Error fetching skills from {repo}: {e}")

        return skills

    async def _parse_github_skill(
        self, client: httpx.AsyncClient, repo: str, skill_name: str, skill_url: str
    ) -> Skill | None:
        """Parse a skill from GitHub.

        Args:
            client: HTTP client
            repo: Repository name
            skill_name: Skill name
            skill_url: Skill directory URL

        Returns:
            Parsed skill or None
        """
        try:
            # Fetch skill directory contents
            response = await client.get(skill_url)
            response.raise_for_status()
            contents = response.json()

            # Look for SKILL.md or README.md
            skill_md = None
            for item in contents:
                if item["name"] in ["SKILL.md", "README.md"]:
                    skill_md = item["download_url"]
                    break

            if not skill_md:
                return None

            # Fetch and parse skill metadata
            response = await client.get(skill_md)
            response.raise_for_status()
            content = response.text

            metadata = self._parse_skill_markdown(content, skill_name)
            skill_id = self._generate_skill_id(f"https://github.com/{repo}", skill_name)

            return Skill(
                id=skill_id,
                metadata=metadata,
                source=SkillSource.GITHUB,
                source_url=f"https://github.com/{repo}",
                installed=skill_id in self.installed_skills,
            )

        except Exception as e:
            logger.debug(f"Error parsing skill {skill_name}: {e}")
            return None

    def _parse_skill_markdown(self, content: str, default_name: str) -> SkillMetadata:
        """Parse skill metadata from markdown content.

        Args:
            content: Markdown content
            default_name: Default skill name

        Returns:
            Skill metadata
        """
        # Extract frontmatter if present
        frontmatter_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
        name = default_name
        description = ""
        tags: list[str] = []

        if frontmatter_match:
            frontmatter = frontmatter_match.group(1)
            for line in frontmatter.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()
                    if key == "name":
                        name = value
                    elif key == "description":
                        description = value
                    elif key == "tags":
                        tags = [t.strip() for t in value.split(",")]

        # Extract description from first paragraph if not in frontmatter
        if not description:
            # Remove frontmatter
            content_without_fm = re.sub(r"^---\n.*?\n---\n", "", content, flags=re.DOTALL)
            # Find first paragraph
            paragraphs = [p.strip() for p in content_without_fm.split("\n\n") if p.strip() and not p.startswith("#")]
            if paragraphs:
                description = paragraphs[0][:200]

        return SkillMetadata(
            name=name,
            description=description,
            tags=tags,
        )

    async def install_skill(self, request: SkillInstallRequest) -> SkillInstallResponse:
        """Install a skill from an external source.

        Args:
            request: Installation request

        Returns:
            Installation response
        """
        try:
            skill_id = self._generate_skill_id(request.source_url, request.skill_name)

            # Check if already installed
            if skill_id in self.installed_skills and not request.force:
                return SkillInstallResponse(
                    success=False,
                    skill=self.installed_skills[skill_id],
                    message="Skill already installed. Use force=True to reinstall.",
                )

            # Install based on source type
            if request.source == SkillSource.GITHUB:
                skill = await self._install_github_skill(request)
            elif request.source == SkillSource.URL:
                skill = await self._install_url_skill(request)
            elif request.source == SkillSource.LOCAL:
                skill = await self._install_local_skill(request)
            else:
                return SkillInstallResponse(
                    success=False, message=f"Unsupported source type: {request.source}", errors=["Invalid source type"]
                )

            if skill:
                skill.installed = True
                skill.installed_at = datetime.now()
                self.installed_skills[skill.id] = skill
                self._save_index()

                return SkillInstallResponse(success=True, skill=skill, message="Skill installed successfully")

            return SkillInstallResponse(success=False, message="Failed to install skill", errors=["Installation failed"])

        except Exception as e:
            logger.error(f"Error installing skill: {e}")
            return SkillInstallResponse(success=False, message=str(e), errors=[str(e)])

    async def _install_github_skill(self, request: SkillInstallRequest) -> Skill | None:
        """Install a skill from GitHub.

        Args:
            request: Installation request

        Returns:
            Installed skill or None
        """
        try:
            # Parse GitHub URL
            parsed = urlparse(request.source_url)
            path_parts = parsed.path.strip("/").split("/")

            if len(path_parts) < 2:
                logger.error(f"Invalid GitHub URL: {request.source_url}")
                return None

            owner, repo = path_parts[0], path_parts[1]
            repo_name = f"{owner}/{repo}"

            async with httpx.AsyncClient(timeout=30.0) as client:
                # Fetch skill from repository
                skills = await self._fetch_github_repo_skills(client, repo_name)

                # Find the requested skill
                target_skill = None
                if request.skill_name:
                    for skill in skills:
                        if skill.metadata.name == request.skill_name:
                            target_skill = skill
                            break
                elif len(skills) == 1:
                    target_skill = skills[0]
                else:
                    logger.error(f"Multiple skills found, please specify skill_name: {[s.metadata.name for s in skills]}")
                    return None

                if not target_skill:
                    logger.error(f"Skill not found: {request.skill_name}")
                    return None

                # Download skill content
                skill_content = await self._download_skill_content(client, repo_name, target_skill.metadata.name)
                target_skill.content = skill_content

                return target_skill

        except Exception as e:
            logger.error(f"Error installing GitHub skill: {e}")
            return None

    async def _download_skill_content(self, client: httpx.AsyncClient, repo: str, skill_name: str) -> dict[str, Any]:
        """Download skill content from GitHub.

        Args:
            client: HTTP client
            repo: Repository name
            skill_name: Skill name

        Returns:
            Skill content
        """
        content: dict[str, Any] = {}

        try:
            # Fetch skill directory
            api_url = f"https://api.github.com/repos/{repo}/contents/skills/{skill_name}"
            response = await client.get(api_url)
            response.raise_for_status()
            items = response.json()

            # Download all files
            for item in items:
                if item["type"] == "file":
                    file_response = await client.get(item["download_url"])
                    file_response.raise_for_status()
                    content[item["name"]] = file_response.text

        except Exception as e:
            logger.debug(f"Error downloading skill content: {e}")

        return content

    async def _install_url_skill(self, request: SkillInstallRequest) -> Skill | None:
        """Install a skill from a URL.

        Args:
            request: Installation request

        Returns:
            Installed skill or None
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(request.source_url)
                response.raise_for_status()

                # Try to parse as JSON (flow definition)
                try:
                    content = response.json()
                    skill_name = request.skill_name or "imported_skill"

                    metadata = SkillMetadata(
                        name=skill_name,
                        description=f"Skill imported from {request.source_url}",
                    )

                    skill_id = self._generate_skill_id(request.source_url, skill_name)

                    return Skill(
                        id=skill_id,
                        metadata=metadata,
                        source=SkillSource.URL,
                        source_url=request.source_url,
                        content={"flow.json": content},
                    )
                except json.JSONDecodeError:
                    # Try to parse as markdown
                    content_text = response.text
                    metadata = self._parse_skill_markdown(content_text, request.skill_name or "imported_skill")

                    skill_id = self._generate_skill_id(request.source_url, metadata.name)

                    return Skill(
                        id=skill_id,
                        metadata=metadata,
                        source=SkillSource.URL,
                        source_url=request.source_url,
                        content={"README.md": content_text},
                    )

        except Exception as e:
            logger.error(f"Error installing URL skill: {e}")
            return None

    async def _install_local_skill(self, request: SkillInstallRequest) -> Skill | None:
        """Install a skill from a local path.

        Args:
            request: Installation request

        Returns:
            Installed skill or None
        """
        try:
            local_path = Path(request.source_url)

            if not local_path.exists():
                logger.error(f"Local path does not exist: {local_path}")
                return None

            content: dict[str, Any] = {}

            # Read all files in the directory
            if local_path.is_dir():
                for file_path in local_path.rglob("*"):
                    if file_path.is_file():
                        rel_path = file_path.relative_to(local_path)
                        with open(file_path) as f:
                            content[str(rel_path)] = f.read()
            else:
                # Single file
                with open(local_path) as f:
                    content[local_path.name] = f.read()

            # Parse metadata
            skill_name = request.skill_name or local_path.stem
            metadata = SkillMetadata(
                name=skill_name,
                description=f"Local skill from {local_path}",
            )

            # Try to find and parse SKILL.md or README.md
            for filename in ["SKILL.md", "README.md"]:
                if filename in content:
                    metadata = self._parse_skill_markdown(content[filename], skill_name)
                    break

            skill_id = self._generate_skill_id(str(local_path), skill_name)

            return Skill(
                id=skill_id,
                metadata=metadata,
                source=SkillSource.LOCAL,
                source_url=str(local_path),
                content=content,
            )

        except Exception as e:
            logger.error(f"Error installing local skill: {e}")
            return None

    def get_installed_skills(self) -> list[Skill]:
        """Get all installed skills.

        Returns:
            List of installed skills
        """
        return list(self.installed_skills.values())

    def get_skill(self, skill_id: str) -> Skill | None:
        """Get a specific skill by ID.

        Args:
            skill_id: Skill ID

        Returns:
            Skill or None if not found
        """
        return self.installed_skills.get(skill_id)

    def uninstall_skill(self, skill_id: str) -> bool:
        """Uninstall a skill.

        Args:
            skill_id: Skill ID

        Returns:
            True if uninstalled successfully
        """
        if skill_id in self.installed_skills:
            del self.installed_skills[skill_id]
            self._save_index()
            return True
        return False

    def update_skill(self, skill_id: str) -> Skill | None:
        """Update an installed skill.

        Args:
            skill_id: Skill ID

        Returns:
            Updated skill or None
        """
        # TODO: Implement skill update logic
        # This would re-fetch the skill from its source and update the content
        logger.warning("Skill update not yet implemented")
        return None
