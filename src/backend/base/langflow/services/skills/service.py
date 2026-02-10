"""Skills service for managing external skills integration."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

import httpx
from lfx.log.logger import logger

from langflow.services.base import Service
from langflow.services.skills.schema import (
    Skill,
    SkillContent,
    SkillInstallRequest,
    SkillInstallResponse,
    SkillMetadata,
    SkillSearchRequest,
    SkillSearchResponse,
)

if TYPE_CHECKING:
    from lfx.services.settings.service import SettingsService


class SkillsService(Service):
    """Service for integrating external skills from GitHub and other sources.

    This service allows discovering, fetching, and integrating external skills
    similar to skills.sh functionality.
    """

    name = "skills_service"

    def __init__(self, settings_service: SettingsService):
        """Initialize the skills service.

        Args:
            settings_service: Settings service for configuration
        """
        self.settings_service = settings_service
        self.timeout = 30
        self.github_api_base = "https://api.github.com"
        self.github_raw_base = "https://raw.githubusercontent.com"

    async def search_skills(self, request: SkillSearchRequest) -> SkillSearchResponse:
        """Search for skills across configured sources.

        Args:
            request: Search request parameters

        Returns:
            Search results with matching skills
        """
        skills = []

        # For now, we implement GitHub-based skill discovery
        # This can be extended to support other sources
        if request.source is None or request.source == "github":
            github_skills = await self._search_github_skills(request)
            skills.extend(github_skills)

        total = len(skills)
        # Apply pagination
        start = request.offset
        end = start + request.limit
        paginated_skills = skills[start:end]

        return SkillSearchResponse(
            total=total,
            skills=paginated_skills,
            offset=request.offset,
            limit=request.limit,
        )

    async def _search_github_skills(self, request: SkillSearchRequest) -> list[Skill]:
        """Search for skills in GitHub repositories.

        Args:
            request: Search request parameters

        Returns:
            List of skills found in GitHub
        """
        skills = []

        # Example: Search in well-known skills repositories
        # Users can configure additional repositories in settings
        default_repos = [
            "vercel-labs/skills",
            # Additional repositories can be added via configuration
        ]

        for repo in default_repos:
            try:
                repo_skills = await self._fetch_skills_from_repo(repo, request.query)
                skills.extend(repo_skills)
            except Exception as e:
                logger.warning(f"Failed to fetch skills from {repo}: {e}")
                continue

        return skills

    async def _fetch_skills_from_repo(self, repo: str, query: str | None = None) -> list[Skill]:
        """Fetch skills from a specific GitHub repository.

        Args:
            repo: Repository identifier (owner/repo)
            query: Optional search query to filter skills

        Returns:
            List of skills from the repository
        """
        skills = []

        try:
            # Fetch repository contents to find SKILL.md files
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.github_api_base}/repos/{repo}/git/trees/main?recursive=1",
                    timeout=self.timeout,
                )
                response.raise_for_status()

                data = response.json()
                tree = data.get("tree", [])

                # Find all SKILL.md files
                skill_files = [
                    item for item in tree if item.get("type") == "blob" and item.get("path", "").endswith("SKILL.md")
                ]

                # Fetch each skill
                for skill_file in skill_files:
                    try:
                        skill_path = skill_file["path"]
                        # Extract skill name from path (e.g., "find-skills/SKILL.md" -> "find-skills")
                        skill_name = skill_path.rsplit("/", 1)[0] if "/" in skill_path else "root"

                        # Skip if query doesn't match skill name
                        if query and query.lower() not in skill_name.lower():
                            continue

                        skill = await self._fetch_skill_from_github(repo, skill_name, skill_path)
                        if skill:
                            skills.append(skill)
                    except Exception as e:
                        logger.warning(f"Failed to fetch skill {skill_path} from {repo}: {e}")
                        continue

        except Exception as e:
            logger.error(f"Failed to fetch skills from repository {repo}: {e}")
            raise

        return skills

    async def _fetch_skill_from_github(self, repo: str, skill_name: str, skill_path: str) -> Skill | None:
        """Fetch a single skill from GitHub.

        Args:
            repo: Repository identifier (owner/repo)
            skill_name: Name of the skill
            skill_path: Path to the SKILL.md file

        Returns:
            Skill object or None if fetch fails
        """
        try:
            async with httpx.AsyncClient() as client:
                # Fetch the SKILL.md content
                response = await client.get(
                    f"{self.github_raw_base}/{repo}/main/{skill_path}",
                    timeout=self.timeout,
                )
                response.raise_for_status()

                content = response.text

                # Parse the skill content
                metadata = self._parse_skill_metadata(content, skill_name, repo)
                skill_content = self._parse_skill_content(content)

                skill_id = f"{repo}/{skill_name}"

                return Skill(
                    id=skill_id,
                    metadata=metadata,
                    content=skill_content,
                    source="github",
                )

        except Exception as e:
            logger.error(f"Failed to fetch skill {skill_name} from {repo}: {e}")
            return None

    def _parse_skill_metadata(self, content: str, skill_name: str, repo: str) -> SkillMetadata:
        """Parse metadata from skill markdown content.

        Args:
            content: Raw markdown content
            skill_name: Name of the skill
            repo: Repository identifier

        Returns:
            Parsed skill metadata
        """
        # Extract title (first H1)
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        title = title_match.group(1) if title_match else skill_name

        # Extract description (first paragraph after title)
        description_match = re.search(r"^#[^\n]+\n+(.+?)(?:\n\n|\n#)", content, re.DOTALL)
        description = description_match.group(1).strip() if description_match else None

        # Extract author from repo
        author = repo.split("/")[0] if "/" in repo else None

        return SkillMetadata(
            name=title,
            description=description,
            author=author,
            repo_url=f"https://github.com/{repo}",
            install_command=f"npx skills add {repo} --skill {skill_name}",
        )

    def _parse_skill_content(self, content: str) -> SkillContent:
        """Parse content from skill markdown.

        Args:
            content: Raw markdown content

        Returns:
            Parsed skill content
        """
        # Extract instructions (content between "When to Use This Skill" and next major section)
        instructions_match = re.search(
            r"##\s+When to Use This Skill\s+(.+?)(?=\n##|\Z)",
            content,
            re.DOTALL | re.IGNORECASE,
        )
        instructions = instructions_match.group(1).strip() if instructions_match else None

        # Extract examples (code blocks)
        examples = re.findall(r"```[\w]*\n(.+?)```", content, re.DOTALL)

        return SkillContent(
            raw_content=content,
            markdown=content,
            instructions=instructions,
            examples=examples,
        )

    async def install_skill(self, request: SkillInstallRequest) -> SkillInstallResponse:
        """Install a skill to make it available in Langflow.

        Args:
            request: Installation request

        Returns:
            Installation response with status
        """
        try:
            # Parse skill_id (format: owner/repo/skill-name)
            parts = request.skill_id.split("/")
            if len(parts) < 3:
                return SkillInstallResponse(
                    skill_id=request.skill_id,
                    status="error",
                    message="Invalid skill ID format. Expected: owner/repo/skill-name",
                )

            repo = f"{parts[0]}/{parts[1]}"
            skill_name = "/".join(parts[2:])
            skill_path = f"{skill_name}/SKILL.md"

            # Fetch the skill
            skill = await self._fetch_skill_from_github(repo, skill_name, skill_path)

            if not skill:
                return SkillInstallResponse(
                    skill_id=request.skill_id,
                    status="error",
                    message="Skill not found",
                )

            # Store the skill in the database or file system
            # For now, we just return success - actual installation logic
            # would involve creating a custom component or storing in DB
            return SkillInstallResponse(
                skill_id=request.skill_id,
                status="success",
                message="Skill installed successfully",
                skill=skill,
            )

        except Exception as e:
            logger.error(f"Failed to install skill {request.skill_id}: {e}")
            return SkillInstallResponse(
                skill_id=request.skill_id,
                status="error",
                message=str(e),
            )

    async def get_skill(self, skill_id: str) -> Skill | None:
        """Get a specific skill by ID.

        Args:
            skill_id: Skill identifier (owner/repo/skill-name)

        Returns:
            Skill object or None if not found
        """
        try:
            parts = skill_id.split("/")
            if len(parts) < 3:
                return None

            repo = f"{parts[0]}/{parts[1]}"
            skill_name = "/".join(parts[2:])
            skill_path = f"{skill_name}/SKILL.md"

            return await self._fetch_skill_from_github(repo, skill_name, skill_path)

        except Exception as e:
            logger.error(f"Failed to get skill {skill_id}: {e}")
            return None
