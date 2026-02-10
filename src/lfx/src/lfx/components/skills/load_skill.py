import subprocess
from pathlib import Path

from lfx.custom.custom_component.component import Component
from lfx.io import BoolInput, DataInput, DropdownInput, MessageTextInput, MultilineInput, Output
from lfx.schema.data import Data


class LoadSkillComponent(Component):
    display_name = "Load Skill"
    description = "Install and load skills from the open agent skills ecosystem."
    documentation: str = "https://skills.sh/"
    icon = "Download"
    name = "LoadSkill"

    inputs = [
        MessageTextInput(
            name="skill_source",
            display_name="Skill Source",
            info="GitHub repo (owner/repo), URL, or local path to skill",
            tool_mode=True,
        ),
        MessageTextInput(
            name="skill_name",
            display_name="Skill Name (Optional)",
            info="Specific skill to install from the repository (leave empty to see available skills)",
            required=False,
            tool_mode=True,
        ),
        DropdownInput(
            name="scope",
            display_name="Installation Scope",
            options=["project", "global"],
            value="project",
            info="Install to project directory or globally for all projects",
            advanced=True,
        ),
        MessageTextInput(
            name="agent",
            display_name="Target Agent",
            info="Specific agent to install for (e.g., 'claude-code', 'codex'). Leave empty for auto-detect.",
            required=False,
            advanced=True,
        ),
        BoolInput(
            name="auto_confirm",
            display_name="Auto Confirm",
            value=False,
            info="Skip confirmation prompts (use with caution)",
            advanced=True,
        ),
        DataInput(
            name="skill_data",
            display_name="Skill Data (from Find Skills)",
            info="Optional: Pass skill data from Find Skills component",
            required=False,
            advanced=True,
        ),
    ]

    outputs = [
        Output(display_name="Result", name="data", method="load_skill"),
    ]

    def load_skill(self) -> Data:
        """Install a skill using the npx skills add command.

        Returns:
            Data object containing installation status and details.
        """
        # Get skill source from input or skill_data
        skill_source = self.skill_source.strip() if isinstance(self.skill_source, str) else ""

        if not skill_source and self.skill_data:
            # Extract from skill_data if available
            data = self.skill_data.data if hasattr(self.skill_data, "data") else self.skill_data
            if isinstance(data, dict):
                if "repository" in data and "name" in data:
                    skill_source = data["repository"]
                    if not self.skill_name:
                        self.skill_name = data["name"]
                elif "full_identifier" in data:
                    parts = data["full_identifier"].split("@")
                    skill_source = parts[0]
                    if len(parts) > 1 and not self.skill_name:
                        self.skill_name = parts[1]

        if not skill_source:
            msg = "Skill source is required (GitHub repo, URL, or local path)"
            self.log(msg)
            return Data(data={"error": msg, "success": False})

        try:
            # Build command
            cmd = ["npx", "skills", "add", skill_source]

            # Add optional flags
            if self.skill_name:
                cmd.extend(["--skill", self.skill_name])

            if self.scope == "global":
                cmd.append("--global")

            if self.agent:
                cmd.extend(["--agent", self.agent])

            if self.auto_confirm:
                cmd.append("--yes")

            # Execute command
            self.log(f"Executing: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )

            # Check result
            success = result.returncode == 0

            if success:
                self.log(f"Successfully installed skill: {skill_source}")
                installed_skills = self._extract_installed_skills(result.stdout)

                return Data(
                    data={
                        "success": True,
                        "skill_source": skill_source,
                        "skill_name": self.skill_name or "all",
                        "scope": self.scope,
                        "agent": self.agent or "auto-detected",
                        "installed_skills": installed_skills,
                        "output": result.stdout,
                    }
                )
            else:
                error_msg = result.stderr or result.stdout or "Installation failed"
                self.log(f"Failed to install skill: {error_msg}")
                return Data(
                    data={
                        "success": False,
                        "skill_source": skill_source,
                        "error": error_msg,
                        "output": result.stdout,
                    }
                )

        except subprocess.TimeoutExpired:
            msg = "Skill installation timed out after 120 seconds"
            self.log(msg)
            return Data(
                data={
                    "success": False,
                    "skill_source": skill_source,
                    "error": msg,
                }
            )
        except FileNotFoundError:
            msg = "npx command not found. Please ensure Node.js and npm are installed."
            self.log(msg)
            return Data(
                data={
                    "success": False,
                    "skill_source": skill_source,
                    "error": msg,
                }
            )
        except Exception as e:
            self.log(f"Error installing skill: {e}")
            return Data(
                data={
                    "success": False,
                    "skill_source": skill_source,
                    "error": str(e),
                }
            )

    def _extract_installed_skills(self, output: str) -> list[str]:
        """Extract installed skill names from command output.

        Args:
            output: Raw stdout from skills add command

        Returns:
            List of installed skill names
        """
        skills = []
        for line in output.split("\n"):
            # Look for common installation success patterns
            if "installed" in line.lower() or "added" in line.lower():
                # Try to extract skill name
                # This is a simple heuristic and may need refinement
                parts = line.strip().split()
                for part in parts:
                    if "@" in part or part.endswith(".md"):
                        skills.append(part)

        return skills
