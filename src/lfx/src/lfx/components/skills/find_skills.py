import subprocess
from typing import Any

from lfx.custom.custom_component.component import Component
from lfx.io import BoolInput, IntInput, MessageTextInput, Output
from lfx.schema.data import Data


class FindSkillsComponent(Component):
    display_name = "Find Skills"
    description = "Search for skills in the open agent skills ecosystem using the skills CLI."
    documentation: str = "https://skills.sh/"
    icon = "Search"
    name = "FindSkills"

    inputs = [
        MessageTextInput(
            name="query",
            display_name="Search Query",
            info="Search term to find relevant skills (e.g., 'react', 'testing', 'deployment')",
            tool_mode=True,
        ),
        IntInput(
            name="max_results",
            display_name="Max Results",
            value=10,
            info="Maximum number of results to return",
            advanced=True,
        ),
        BoolInput(
            name="include_internal",
            display_name="Include Internal Skills",
            value=False,
            info="Include internal/work-in-progress skills in search results",
            advanced=True,
        ),
    ]

    outputs = [
        Output(display_name="Skills", name="data", method="find_skills"),
    ]

    def find_skills(self) -> Data:
        """Search for skills using the npx skills find command.

        Returns:
            Data object containing search results with skill names, descriptions, and install commands.
        """
        query = self.query.strip() if isinstance(self.query, str) else ""

        try:
            # Build command
            cmd = ["npx", "skills", "find"]
            if query:
                cmd.append(query)

            # Set environment variables if needed
            env = None
            if self.include_internal:
                import os

                env = os.environ.copy()
                env["INSTALL_INTERNAL_SKILLS"] = "1"

            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                env=env,
                check=False,
            )

            # Parse output
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout or "Unknown error occurred"
                self.log(f"Skills search failed: {error_msg}")
                return Data(
                    data={
                        "error": error_msg,
                        "query": query,
                        "results": [],
                    }
                )

            # Parse the output to extract skill information
            skills = self._parse_skills_output(result.stdout)

            # Limit results
            if self.max_results > 0:
                skills = skills[: self.max_results]

            return Data(
                data={
                    "query": query,
                    "count": len(skills),
                    "results": skills,
                    "raw_output": result.stdout,
                }
            )

        except subprocess.TimeoutExpired:
            self.log("Skills search timed out after 30 seconds")
            return Data(
                data={
                    "error": "Search timed out",
                    "query": query,
                    "results": [],
                }
            )
        except FileNotFoundError:
            msg = "npx command not found. Please ensure Node.js and npm are installed."
            self.log(msg)
            return Data(
                data={
                    "error": msg,
                    "query": query,
                    "results": [],
                }
            )
        except Exception as e:
            self.log(f"Error searching for skills: {e}")
            return Data(
                data={
                    "error": str(e),
                    "query": query,
                    "results": [],
                }
            )

    def _parse_skills_output(self, output: str) -> list[dict[str, Any]]:
        """Parse the output from npx skills find command.

        Args:
            output: Raw stdout from the skills find command

        Returns:
            List of dictionaries containing skill information
        """
        skills = []
        lines = output.strip().split("\n")

        # Skip header lines
        skill_data = None
        for line in lines:
            line = line.strip()

            # Skip empty lines and header
            if not line or line.startswith("Install with"):
                continue

            # Skill identifier line (e.g., "vercel-labs/agent-skills@skill-name")
            if "@" in line and "/" in line:
                if skill_data:
                    skills.append(skill_data)

                parts = line.split("@")
                repo = parts[0].strip()
                skill_name = parts[1].strip() if len(parts) > 1 else ""

                skill_data = {
                    "name": skill_name,
                    "repository": repo,
                    "full_identifier": line,
                    "install_command": f"npx skills add {repo}@{skill_name}",
                }

            # URL line (e.g., "└ https://skills.sh/...")
            elif skill_data and line.startswith("└") and "https://" in line:
                url = line.replace("└", "").strip()
                skill_data["url"] = url

        # Add the last skill if exists
        if skill_data:
            skills.append(skill_data)

        return skills
