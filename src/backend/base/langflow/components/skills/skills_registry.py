"""Skills Registry component for discovering external skills."""

from __future__ import annotations

from langflow.custom import Component
from langflow.io import MessageTextInput, Output, StrInput
from langflow.schema import Data
from langflow.services.skills.manager import SkillsManager


class SkillsRegistryComponent(Component):
    """Component for discovering and searching external skills."""

    display_name = "Skills Registry"
    description = "Discover and search for external skills from repositories like skills.sh"
    icon = "search"
    name = "SkillsRegistry"

    inputs = [
        MessageTextInput(
            name="query",
            display_name="Search Query",
            info="Search query to find skills (e.g., 'react', 'testing', 'deployment')",
            required=True,
        ),
        StrInput(
            name="source",
            display_name="Source Filter",
            info="Filter by source type (github, url, local). Leave empty to search all sources.",
            options=["", "github", "url", "local"],
            value="",
            advanced=True,
        ),
    ]

    outputs = [
        Output(display_name="Skills", name="skills", method="search_skills"),
    ]

    async def search_skills(self) -> Data:
        """Search for skills based on the query.

        Returns:
            Data object containing search results
        """
        manager = SkillsManager()

        source_filter = self.source if self.source else None
        results = await manager.search_skills(query=self.query, source=source_filter)

        # Convert results to Data format
        skills_data = []
        for skill in results.skills:
            skill_dict = {
                "id": skill.id,
                "name": skill.metadata.name,
                "description": skill.metadata.description,
                "source": skill.source.value,
                "source_url": skill.source_url,
                "installed": skill.installed,
                "tags": skill.metadata.tags,
            }
            skills_data.append(skill_dict)

        return Data(
            data={
                "skills": skills_data,
                "total": results.total,
                "query": results.query,
            }
        )
