"""Skills Installer component for installing external skills."""

from __future__ import annotations

from langflow.custom import Component
from langflow.io import BoolInput, MessageTextInput, Output, StrInput
from langflow.schema import Data
from langflow.services.skills.manager import SkillsManager
from langflow.services.skills.models import SkillInstallRequest, SkillSource


class SkillsInstallerComponent(Component):
    """Component for installing external skills."""

    display_name = "Skills Installer"
    description = "Install external skills from GitHub, URLs, or local paths"
    icon = "download"
    name = "SkillsInstaller"

    inputs = [
        StrInput(
            name="source_type",
            display_name="Source Type",
            info="Type of skill source",
            options=["github", "url", "local"],
            value="github",
            required=True,
        ),
        MessageTextInput(
            name="source_url",
            display_name="Source URL/Path",
            info="GitHub URL (e.g., https://github.com/vercel-labs/skills), direct URL, or local path",
            required=True,
        ),
        MessageTextInput(
            name="skill_name",
            display_name="Skill Name",
            info="Specific skill name (required if repository contains multiple skills)",
            value="",
            advanced=True,
        ),
        BoolInput(
            name="force_reinstall",
            display_name="Force Reinstall",
            info="Force reinstall if skill is already installed",
            value=False,
            advanced=True,
        ),
    ]

    outputs = [
        Output(display_name="Result", name="result", method="install_skill"),
    ]

    async def install_skill(self) -> Data:
        """Install a skill from the specified source.

        Returns:
            Data object containing installation result
        """
        manager = SkillsManager()

        # Create install request
        request = SkillInstallRequest(
            source=SkillSource(self.source_type),
            source_url=self.source_url,
            skill_name=self.skill_name if self.skill_name else None,
            force=self.force_reinstall,
        )

        # Install the skill
        response = await manager.install_skill(request)

        # Convert response to Data format
        result_data = {
            "success": response.success,
            "message": response.message,
            "errors": response.errors,
        }

        if response.skill:
            result_data["skill"] = {
                "id": response.skill.id,
                "name": response.skill.metadata.name,
                "description": response.skill.metadata.description,
                "source": response.skill.source.value,
                "source_url": response.skill.source_url,
                "installed": response.skill.installed,
                "installed_at": str(response.skill.installed_at) if response.skill.installed_at else None,
            }

        return Data(data=result_data)
